import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:photo_view/photo_view.dart';

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
  String _description = '';
  List<String> _tickers = [];
  final TextEditingController _controller = TextEditingController();

  // 환경 변수 직접 포함
  final String apiUrl = 'http://192.168.0.5:5000/api/get_reviewed_tickers';
  final String descriptionApiUrl = 'http://192.168.0.5:5000/generate_description';
  final String executeCommandApiUrl = 'http://192.168.0.5:5000/execute_stock_command';

  Future<void> fetchReviewedTickers() async {
    try {
      final response = await http.get(Uri.parse(apiUrl));
      if (response.statusCode == 200) {
        final List<dynamic> tickers = json.decode(response.body);
        setState(() {
          _tickers = List<String>.from(tickers);
        });
      } else {
        setState(() {
          _message = 'Error occurred while fetching tickers: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _message = 'Error occurred while fetching tickers: $e';
      });
    }
  }

  Future<void> fetchImages(String stockTicker) async {
    try {
      final response = await http.get(Uri.parse('https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images'));
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
          await generateDescription(stockTicker); // 그래프 설명 생성
        } else {
          setState(() {
            _comparisonImageUrl = '';
            _resultImageUrl = '';
            _message = '해당 주식 티커에 대한 이미지를 찾을 수 없습니다';
          });
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

  Future<void> generateDescription(String stockTicker) async {
    try {
      final response = await http.post(
        Uri.parse(descriptionApiUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'stock_ticker': stockTicker}),
      );

      if (response.statusCode == 200) {
        final responseBody = json.decode(response.body);
        final description = responseBody['description'];
        setState(() {
          _description = description;
        });
      } else {
        setState(() {
          _description = '설명 생성 실패: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _description = '오류 발생: $e';
      });
    }
  }

  Future<void> executeStockCommand(String stockTicker) async {
    try {
      final response = await http.post(
        Uri.parse(executeCommandApiUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'stock_ticker': stockTicker}),
      );

      if (response.statusCode == 200) {
        final responseBody = json.decode(response.body);
        setState(() {
          _message = responseBody['message'];
        });
      } else {
        setState(() {
          _message = '명령 실행 실패: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _message = '오류 발생: $e';
      });
    }
  }

  void _openImage(BuildContext context, String imageUrl) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ImageScreen(imageUrl: imageUrl),
      ),
    );
  }

  @override
  void initState() {
    super.initState();
    fetchReviewedTickers();
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
                    executeStockCommand(_controller.text.toUpperCase());
                  },
                ),
              ),
              ElevatedButton(
                onPressed: () {
                  fetchImages(_controller.text.toUpperCase());
                  executeStockCommand(_controller.text.toUpperCase());
                },
                child: Text('Fetch Stock Images'),
              ),
              SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(8.0),
                child: Text(
                  'Reviewed Stocks:',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8.0),
                child: Wrap(
                  spacing: 5.0,
                  runSpacing: 5.0,
                  children: _tickers.map((ticker) => GestureDetector(
                    onTap: () {
                      fetchImages(ticker);
                    },
                    child: Text(
                      ticker,
                      style: TextStyle(fontSize: 14, color: Colors.blue, decoration: TextDecoration.underline),
                    ),
                  )).toList(),
                ),
              ),
              SizedBox(height: 20),
              _comparisonImageUrl.isNotEmpty
                  ? GestureDetector(
                      onTap: () => _openImage(context, _comparisonImageUrl),
                      child: Image.network(
                        _comparisonImageUrl,
                        errorBuilder: (context, error, stackTrace) {
                          return Text('Failed to load comparison image');
                        },
                      ),
                    )
                  : Container(),
              SizedBox(height: 20),
              _resultImageUrl.isNotEmpty
                  ? GestureDetector(
                      onTap: () => _openImage(context, _resultImageUrl),
                      child: Image.network(
                        _resultImageUrl,
                        errorBuilder: (context, error, stackTrace) {
                          return Text('Failed to load result image');
                        },
                      ),
                    )
                  : Container(),
              SizedBox(height: 20),
              _message.isNotEmpty
                  ? Text(
                      _message,
                      style: TextStyle(fontSize: 16, color: Colors.red),
                    )
                  : Container(),
              SizedBox(height: 20),
              _description.isNotEmpty
                  ? Text(
                      _description,
                      style: TextStyle(fontSize: 16, color: Colors.green),
                    )
                  : Container(),
            ],
          ),
        ),
      ),
    );
  }
}

class ImageScreen extends StatelessWidget {
  final String imageUrl;

  ImageScreen({required this.imageUrl});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Image Preview'),
      ),
      body: Center(
        child: PhotoView(
          imageProvider: NetworkImage(imageUrl),
          errorBuilder: (context, error, stackTrace) {
            return Text('Failed to load image');
          },
        ),
      ),
    );
  }
}

// flutter devices

// flutter run -d R3CX404VPHE

// flutter run -d chrome