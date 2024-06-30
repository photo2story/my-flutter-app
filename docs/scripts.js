$(function() {
    const stockInput = $('#stockName');
    const searchReviewButton = $('#searchReviewButton');
    const reviewList = $('#reviewList');
    const tickerList = $('#ticker-list');

    function fetchImages(stockTicker) {
        const apiUrl = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images';

        $.ajax({
            url: apiUrl,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                const comparisonFile = data.find(file => file.name === `comparison_${stockTicker}_VOO.png`);
                const resultFile = data.find(file => file.name === `result_mpl_${stockTicker}.png`);

                reviewList.empty();

                if (comparisonFile && resultFile) {
                    reviewList.append(`
                        <div class="review">
                            <h3>${stockTicker} vs VOO</h3>
                            <img src="${comparisonFile.download_url}" alt="${stockTicker} vs VOO" style="width: 100%;">
                            <img src="${resultFile.download_url}" alt="${stockTicker} Result" style="width: 100%; margin-top: 20px;">
                        </div>
                    `);
                } else {
                    alert(`해당 주식 티커에 대한 이미지를 찾을 수 없습니다`);
                }
            },
            error: function() {
                alert('이미지를 불러오는 중 오류가 발생했습니다.');
            }
        });
    }

    searchReviewButton.click(function() {
        const stockTicker = stockInput.val().toUpperCase();
        if (stockTicker) {
            fetchImages(stockTicker);
        }
    });

    stockInput.on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            searchReviewButton.click();
            return false;
        }
    });

    // 주식 티커 목록 가져오기 및 표시
    const apiUrl = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images';
    $.ajax({
        url: apiUrl,
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            const tickers = data.map(file => file.name.replace('comparison_', '').replace('_VOO.png', ''))
                                .filter((value, index, self) => self.indexOf(value) === index)
                                .sort();
            tickers.forEach(ticker => {
                tickerList.append(`<span class="ticker-item" onclick="fetchImages('${ticker}')">${ticker}</span>`);
            });
        },
        error: function() {
            alert('주식 티커 목록을 불러오는 중 오류가 발생했습니다.');
        }
    });
});
