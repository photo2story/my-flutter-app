$(function() {
    const stockInput = $('#stockName');
    const searchReviewButton = $('#searchReviewButton');
    const reviewList = $('#reviewList');
    const tickerListContainer = $('#ticker-list');
    const searchedTickersContainer = $('#searched-tickers');

    function fetchImages(stockTicker, clearReviewList = false) {
        const apiUrl = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images';

        $.ajax({
            url: apiUrl,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                const comparisonFile = data.find(file => file.name === `comparison_${stockTicker}_VOO.png`);
                const resultFile = data.find(file => file.name === `result_mpl_${stockTicker}.png`);

                if (clearReviewList) {
                    reviewList.empty();
                }

                if (comparisonFile && resultFile) {
                    reviewList.append(`
                        <div class="review">
                            <h3>${stockTicker} vs VOO</h3>
                            <div class="chart-container">
                                <img src="${comparisonFile.download_url}" alt="${stockTicker} vs VOO" class="responsive-img">
                            </div>
                            <div class="chart-container" style="margin-top: 20px;">
                                <img src="${resultFile.download_url}" alt="${stockTicker} Result" class="responsive-img">
                            </div>
                        </div>
                    `);
                    console.log(`Successfully fetched review for ${stockTicker}.`);
                } else {
                    console.log(`Unable to find images for the stock ticker ${stockTicker}.`);
                    saveSearchedTicker(stockTicker);
                    displaySearchedTickers();
                }
            },
            error: function() {
                console.log('Error occurred while fetching images.');
            }
        });
    }

    function saveSearchedTicker(ticker) {
        let searchedTickers = JSON.parse(localStorage.getItem('searchedTickers')) || {};
        if (searchedTickers[ticker]) {
            searchedTickers[ticker]++;
        } else {
            searchedTickers[ticker] = 1;
        }
        localStorage.setItem('searchedTickers', JSON.stringify(searchedTickers));
    }

    function displaySearchedTickers() {
        let searchedTickers = JSON.parse(localStorage.getItem('searchedTickers')) || {};
        searchedTickersContainer.empty();
        searchedTickersContainer.append('<h2>Searched Stocks</h2>');
        for (let ticker in searchedTickers) {
            searchedTickersContainer.append(`<span class="ticker-item">${ticker} (${searchedTickers[ticker]})</span>`);
        }
    }

    function loadTickerList() {
        const apiUrl = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images';

        $.ajax({
            url: apiUrl,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                const tickers = data
                    .filter(file => file.name.startsWith('comparison_') && file.name.endsWith('_VOO.png'))
                    .map(file => file.name.replace('comparison_', '').replace('_VOO.png', ''))
                    .sort(); // 알파벳 순으로 정렬

                tickerListContainer.empty();

                tickers.forEach(ticker => {
                    tickerListContainer.append(`<span class="ticker-item">${ticker}</span>`);
                });

                $('.ticker-item').on('click', function() {
                    const stockTicker = $(this).text();
                    stockInput.val(stockTicker);
                    fetchImages(stockTicker, true); // 특정 주식을 클릭했을 때 리뷰 목록 초기화
                });

                // 모든 검토된 주식을 초기화면에 표시
                tickers.forEach(ticker => {
                    fetchImages(ticker, false); // 모든 티커에 대해 reviewList를 비우지 않음
                });
            },
            error: function() {
                console.log('Error occurred while loading ticker list.');
            }
        });
    }

    searchReviewButton.click(function() {
        const stockTicker = stockInput.val().toUpperCase();
        if (stockTicker) {
            fetchImages(stockTicker, true); // 검색 시 리뷰 목록 초기화
        }
    });

    stockInput.on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            searchReviewButton.click();
            return false;
        }
    });

    loadTickerList(); // 페이지 로드 시 티커 목록 불러오기
    displaySearchedTickers(); // 페이지 로드 시 검색된 티커 목록 불러오기
});
