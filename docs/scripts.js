$(function() {
    const stockInput = $('#stockName');
    const searchReviewButton = $('#searchReviewButton');
    const reviewList = $('#reviewList');
    const tickerListContainer = $('#ticker-list');

    function fetchImages(stockTicker) {
        const apiUrl = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images';

        $.ajax({
            url: apiUrl,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                // 티커 이름과 회사 이름이 포함된 파일도 검색
                const comparisonFile = data.find(file => file.name.includes(`comparison_${stockTicker}_`) && file.name.includes('_VOO.png'));
                const resultFile = data.find(file => file.name.includes(`result_mpl_${stockTicker}.png`));

                reviewList.empty();

                if (comparisonFile && resultFile) {
                    reviewList.append(`
                        <div class="review">
                            <h3>${stockTicker} vs VOO</h3>
                            <img src="${comparisonFile.download_url}" alt="${stockTicker} vs VOO" style="width: 100%;">
                            <img src="${resultFile.download_url}" alt="${stockTicker} Result" style="width: 100%; margin-top: 20px;">
                        </div>
                    `);
                    alert(`${stockTicker} 리뷰를 성공적으로 불러왔습니다.`);
                } else {
                    alert(`해당 주식 티커에 대한 이미지를 찾을 수 없습니다`);
                }
            },
            error: function() {
                alert('이미지를 불러오는 중 오류가 발생했습니다.');
            }
        });
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
                    .map(file => file.name.replace('comparison_', '').replace('_VOO.png', '').split('_')[0])
                    .sort();

                tickerListContainer.empty();

                tickers.forEach(ticker => {
                    tickerListContainer.append(`<span class="ticker-item">${ticker}</span>`);
                });

                $('.ticker-item').on('click', function() {
                    const stockTicker = $(this).text();
                    stockInput.val(stockTicker);
                    fetchImages(stockTicker);
                });
            },
            error: function() {
                alert('티커 목록을 불러오는 중 오류가 발생했습니다.');
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

    loadTickerList(); // 페이지 로드 시 티커 목록을 로드합니다.
});
