import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Stock Comparison Review',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _comparisonImageUrl = '';
  String _resultImageUrl = '';
  String _message = '';
  final TextEditingController _controller = TextEditingController();
  List<String> _tickers = [];

  Future<void> fetchImages(String stockTicker) async {
    final apiUrl = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images';
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
          await sendToFlaskServer('$stockTicker 리뷰했습니다.');
        } else {
          setState(() {
            _comparisonImageUrl = '';
            _resultImageUrl = '';
            _message = '해당 주식 티커에 대한 이미지를 찾을 수 없습니다';
          });
          await sendToFlaskServer('$stockTicker 리뷰 추가가 필요합니다.');
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

  Future<void> sendToFlaskServer(String message) async {
    final apiUrl = 'http://127.0.0.1:5000/send_discord_message'; // Flask 서버 URL로 수정하세요
    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'message': message}),
      );

      if (response.statusCode != 200) {
        print('Failed to send message to Flask server: ${response.statusCode}');
      }
    } catch (e) {
      print('Error sending message to Flask server: $e');
    }
  }

  Future<void> fetchTickers() async {
    final apiUrl = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images';
    try {
      final response = await http.get(Uri.parse(apiUrl));
      if (response.statusCode == 200) {
        final List<dynamic> files = json.decode(response.body);
        final tickers = files
            .where((file) => file['name'].toString().startsWith('comparison_') && file['name'].toString().endsWith('_VOO.png'))
            .map((file) => file['name'].toString().replaceAll('comparison_', '').replaceAll('_VOO.png', ''))
            .toList();

        setState(() {
          _tickers = tickers.cast<String>();
        });
      } else {
        print('Failed to fetch tickers: ${response.statusCode}');
      }
    } catch (e) {
      print('Error fetching tickers: $e');
    }
  }

  @override
  void initState() {
    super.initState();
    fetchTickers();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Stock Comparison Review'),
      ),
      body: Center(
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: TextField(
                  controller: _controller,
                  textCapitalization: TextCapitalization.characters,
                  decoration: InputDecoration(
                    border: OutlineInputBorder(),
                    labelText: 'Enter Stock Ticker',
                  ),
                  onChanged: (value) {
                    _controller.value = TextEditingValue(
                      text: value.toUpperCase(),
                      selection: _controller.selection,
                    );
                  },
                  onSubmitted: (value) {
                    fetchImages(_controller.text.toUpperCase());
                  },
                ),
              ),
              ElevatedButton(
                onPressed: () {
                  fetchImages(_controller.text.toUpperCase());
                },
                child: Text('Fetch Stock Images'),
              ),
              SizedBox(height: 20),
              Wrap(
                children: _tickers.map((ticker) {
                  return Padding(
                    padding: const EdgeInsets.all(4.0),
                    child: InkWell(
                      onTap: () {
                        _controller.text = ticker;
                        fetchImages(ticker);
                      },
                      child: Text(
                        ticker,
                        style: TextStyle(
                          color: Colors.blue,
                          decoration: TextDecoration.underline,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              SizedBox(height: 20),
              _comparisonImageUrl.isNotEmpty
                  ? Image.network(
                      _comparisonImageUrl,
                      errorBuilder: (context, error, stackTrace) {
                        return Text('Failed to load comparison image');
                      },
                    )
                  : Container(),
              SizedBox(height: 20),
              _resultImageUrl.isNotEmpty
                  ? Image.network(
                      _resultImageUrl,
                      errorBuilder: (context, error, stackTrace) {
                        return Text('Failed to load result image');
                      },
                    )
                  : Container(),
              SizedBox(height: 20),
              _message.isNotEmpty
                  ? Text(
                      _message,
                      style: TextStyle(fontSize: 16, color: Colors.red),
                    )
                  : Container(),
            ],
          ),
        ),
      ),
    );
  }
}
