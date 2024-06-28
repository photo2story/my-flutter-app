Future<void> fetchImages(String stockTicker) async {
  final apiUrl = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/my-flask-app';
  try {
    final response = await http.get(Uri.parse(apiUrl));
    if (response.statusCode == 200) {
      final List<dynamic> files = json.decode(response.body);
      final comparisonFile = files.firstWhere(
          (file) => file['name'] == 'comparison_${stockTicker}_VOO.png',
          orElse: () => null);
      final resultFile = files.firstWhere(
          (file) => file['name'] == 'result_mpl_${stockTicker}.png',
          orElse: () => null);

      if (comparisonFile != null && resultFile != null) {
        setState(() {
          _comparisonImageUrl = comparisonFile['download_url'];
          _resultImageUrl = resultFile['download_url'];
          _message = '';
        });
        await sendDiscordMessage('$stockTicker 리뷰했습니다.');
      } else {
        setState(() {
          _comparisonImageUrl = '';
          _resultImageUrl = '';
          _message = '해당 주식 티커에 대한 이미지를 찾을 수 없습니다';
        });
        await sendDiscordMessage('$stockTicker 리뷰 추가가 필요합니다.');
      }
    } else {
      setState(() {
        _comparisonImageUrl = '';
        _resultImageUrl = '';
        _message = 'GitHub API 호출 실패: ${response.statusCode}';
      });
    }
  } catch (e) {
    setState(() {
      _comparisonImageUrl = '';
      _resultImageUrl = '';
      _message = '오류 발생: $e';
    });
  }
}

Future<void> sendDiscordMessage(String message) async {
  final apiUrl = 'http://127.0.0.1:5000/send_discord_message'; // Flask 서버 URL로 수정하세요
  try {
    final response = await http.post(
      Uri.parse(apiUrl),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'message': message}),
    );

    if (response.statusCode != 200) {
      print('Failed to send Discord message: ${response.statusCode}');
    }
  } catch (e) {
    print('Error sending Discord message: $e');
  }
}
