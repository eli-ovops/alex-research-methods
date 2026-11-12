#pragma once
 
#include <cstdint>
#include <optional>
#include <string>
#include <vector>
 
namespace bybit {
 
// One row of OHLCV data, normalised to our internal format.
struct Kline {
    int64_t open_time_ms;   // UTC milliseconds, start of the bar
    double  open;
    double  high;
    double  low;
    double  close;
    double  volume;         // base asset (BTC)
    double  turnover;       // quote asset (USDT)
};
 
// One funding rate observation.
struct FundingRate {
    int64_t timestamp_ms;   // UTC ms, when funding was applied
    double  rate;           // decimal, e.g. 0.0001 == 0.01% == 1bp
};
 
// Bybit kline interval enum. We only support what we use.
enum class Interval {
    Hour1,
    Hour4,
    Day1,
};
 
const char* interval_to_string(Interval iv);
 
class BybitClient {
public:
    // Base URL is configurable for testing against testnet.
    explicit BybitClient(std::string base_url = "https://api.bybit.com");
    ~BybitClient();
 
    // Disable copy — owns libcurl handle.
    BybitClient(const BybitClient&)            = delete;
    BybitClient& operator=(const BybitClient&) = delete;
 
    // Fetch klines for [start_ms, end_ms]. Pagination handled internally.
    // Returns rows in ascending time order. Empty vector means failure
    // (we log to stderr).
    std::vector<Kline> fetch_klines(
        const std::string& symbol,
        Interval           interval,
        int64_t            start_ms,
        int64_t            end_ms);
 
    // Fetch funding rate history for [start_ms, end_ms].
    std::vector<FundingRate> fetch_funding_history(
        const std::string& symbol,
        int64_t            start_ms,
        int64_t            end_ms);
 
private:
    // Internal: perform GET request, return body as string.
    std::optional<std::string> http_get(const std::string& url);
 
    std::string base_url_;
    void*       curl_;  // CURL* — kept opaque to keep curl out of header
};
 
}  // namespace bybit