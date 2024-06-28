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
  String _imageUrl = '';
  String _message = '';
  final TextEditingController _controller = TextEditingController();

  Future<void> fetchGitHubFiles() async {
    final apiUrl = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/my-flask-app';
    try {
      final response = await http.get(Uri.parse(apiUrl));
      if (response.statusCode == 200) {
        final List<dynamic> files = json.decode(response.body);
        final pngFiles = files.where((file) => file['name'].endsWith('.png')).map((file) => file['name']).toList();
        if (pngFiles.isNotEmpty) {
          setState(() {
            _imageUrl = 'https://github.com/photo2story/my-flutter-app/blob/main/my-flask-app/${pngFiles[0]}?raw=true';
            _message = '';
          });
        } else {
          setState(() {
            _imageUrl = '';
            _message = 'PNG 파일이 없습니다';
          });
        }
      } else {
        setState(() {
          _imageUrl = '';
          _message = 'GitHub API 호출 실패: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _imageUrl = '';
        _message = '오류 발생: $e';
      });
    }
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
                ),
              ),
              ElevatedButton(
                onPressed: () {
                  fetchGitHubFiles();
                },
                child: Text('Fetch GitHub Files'),
              ),
              SizedBox(height: 20),
              _imageUrl.isNotEmpty
                  ? Image.network(
                      _imageUrl,
                      errorBuilder: (context, error, stackTrace) {
                        return Text('Failed to load image');
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
