#include "bybit_client.h"

#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <sstream>
#include <thread>
 
#include <curl/curl.h>
#include <nlohmann/json.hpp>
 
namespace bybit {
 
using json = nlohmann::json;
 
const char* interval_to_string(Interval iv) {
    switch (iv) {
        case Interval::Hour1: return "60";
        case Interval::Hour4: return "240";
        case Interval::Day1:  return "D";
    }
    return "60";
}
 
// libcurl write callback — appends bytes into a std::string passed via userdata.
static size_t write_callback(char* ptr, size_t size, size_t nmemb, void* userdata) {
    auto* s = static_cast<std::string*>(userdata);
    s->append(ptr, size * nmemb);
    return size * nmemb;
}
 
// -------------------------------------------------------------------------
// Construction
// -------------------------------------------------------------------------
BybitClient::BybitClient(std::string base_url)
    : base_url_(std::move(base_url)), curl_(nullptr) {
    // curl_global_init is safe to call multiple times.
    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl_ = curl_easy_init();
    if (!curl_) {
        throw std::runtime_error("curl_easy_init failed");
    }
}
 
BybitClient::~BybitClient() {
    if (curl_) {
        curl_easy_cleanup(static_cast<CURL*>(curl_));
    }
    // We don't curl_global_cleanup — not safe in libraries with multiple users.
}
 
// -------------------------------------------------------------------------
// HTTP GET
// -------------------------------------------------------------------------
std::optional<std::string> BybitClient::http_get(const std::string& url) {
    CURL* curl = static_cast<CURL*>(curl_);
    std::string response;
 
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30L);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_USERAGENT, "funding_harvester/1.0");
 
    CURLcode rc = curl_easy_perform(curl);
    if (rc != CURLE_OK) {
        std::cerr << "curl error: " << curl_easy_strerror(rc) << "\n";
        return std::nullopt;
    }
 
    long http_code = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
    if (http_code != 200) {
        std::cerr << "HTTP " << http_code << " for " << url << "\n";
        std::cerr << "body: " << response.substr(0, 500) << "\n";
        return std::nullopt;
    }
 
    return response;
}
 
// -------------------------------------------------------------------------
// Klines
// -------------------------------------------------------------------------
std::vector<Kline> BybitClient::fetch_klines(
    const std::string& symbol,
    Interval           interval,
    int64_t            start_ms,
    int64_t            end_ms)
{
    std::vector<Kline> out;
    int64_t cursor_end = end_ms;  // we walk backward from end → start
    const int kPageLimit = 1000;
 
    while (cursor_end > start_ms) {
        std::ostringstream url;
        url << base_url_ << "/v5/market/kline"
            << "?category=linear"
            << "&symbol="   << symbol
            << "&interval=" << interval_to_string(interval)
            << "&start="    << start_ms
            << "&end="      << cursor_end
            << "&limit="    << kPageLimit;
 
        auto body = http_get(url.str());
        if (!body) break;
 
        json j;
        try {
            j = json::parse(*body);
        } catch (const std::exception& e) {
            std::cerr << "JSON parse error: " << e.what() << "\n";
            break;
        }
 
        // Bybit envelope: { retCode: 0, result: { list: [[...], ...] } }
        if (j.value("retCode", -1) != 0) {
            std::cerr << "Bybit error: " << j.dump() << "\n";
            break;
        }
 
        const auto& list = j["result"]["list"];
        if (list.empty()) break;
 
        // Bybit returns newest first. We collect, then reverse at the end.
        // Each row: [start, open, high, low, close, volume, turnover] as strings.
        int64_t oldest_in_page = cursor_end;
        for (const auto& row : list) {
            Kline k;
            k.open_time_ms = std::stoll(row[0].get<std::string>());
            k.open         = std::stod(row[1].get<std::string>());
            k.high         = std::stod(row[2].get<std::string>());
            k.low          = std::stod(row[3].get<std::string>());
            k.close        = std::stod(row[4].get<std::string>());
            k.volume       = std::stod(row[5].get<std::string>());
            k.turnover     = std::stod(row[6].get<std::string>());
 
            if (k.open_time_ms >= start_ms && k.open_time_ms <= end_ms) {
                out.push_back(k);
            }
            if (k.open_time_ms < oldest_in_page) {
                oldest_in_page = k.open_time_ms;
            }
        }
 
        // Advance cursor: next request ends 1ms before the oldest we got.
        if (oldest_in_page <= start_ms) break;
        cursor_end = oldest_in_page - 1;
 
        // Polite rate-limiting.
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
 
    // Sort ascending — final guarantee for the caller.
    std::sort(out.begin(), out.end(), [](const Kline& a, const Kline& b) {
        return a.open_time_ms < b.open_time_ms;
    });
    return out;
}
 
// -------------------------------------------------------------------------
// Funding history
// -------------------------------------------------------------------------
std::vector<FundingRate> BybitClient::fetch_funding_history(
    const std::string& symbol,
    int64_t            start_ms,
    int64_t            end_ms)
{
    std::vector<FundingRate> out;
    int64_t cursor_end = end_ms;
    const int kPageLimit = 200;  // funding endpoint cap
 
    while (cursor_end > start_ms) {
        std::ostringstream url;
        url << base_url_ << "/v5/market/funding/history"
            << "?category=linear"
            << "&symbol="    << symbol
            << "&startTime=" << start_ms
            << "&endTime="   << cursor_end
            << "&limit="     << kPageLimit;
 
        auto body = http_get(url.str());
        if (!body) break;
 
        json j;
        try { j = json::parse(*body); }
        catch (const std::exception& e) {
            std::cerr << "JSON parse error: " << e.what() << "\n";
            break;
        }
 
        if (j.value("retCode", -1) != 0) {
            std::cerr << "Bybit error: " << j.dump() << "\n";
            break;
        }
 
        const auto& list = j["result"]["list"];
        if (list.empty()) break;
 
        int64_t oldest_in_page = cursor_end;
        for (const auto& row : list) {
            FundingRate f;
            f.timestamp_ms = std::stoll(row["fundingRateTimestamp"].get<std::string>());
            f.rate         = std::stod(row["fundingRate"].get<std::string>());
 
            if (f.timestamp_ms >= start_ms && f.timestamp_ms <= end_ms) {
                out.push_back(f);
            }
            if (f.timestamp_ms < oldest_in_page) {
                oldest_in_page = f.timestamp_ms;
            }
        }
 
        if (oldest_in_page <= start_ms) break;
        cursor_end = oldest_in_page - 1;
 
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
 
    std::sort(out.begin(), out.end(), [](const FundingRate& a, const FundingRate& b) {
        return a.timestamp_ms < b.timestamp_ms;
    });
    return out;
}
 
}  // namespace bybit