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
  String _response = '';
  String _imageUrl = '';

  final TextEditingController _controller = TextEditingController();

  Future<void> sendStockRequest(String stockName) async {
    final response = await http.post(
      Uri.parse('http://127.0.0.1:5000/execute_discord_command'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'command': 'stock',
        'stock_name': stockName,
      }),
    );

    if (response.statusCode == 200) {
      setState(() {
        _response = response.body;
        _imageUrl = 'http://127.0.0.1:5000/static/images/comparison_${stockName.toUpperCase()}_VOO.png';
      });
    } else {
      setState(() {
        _response = 'Error: ${response.reasonPhrase}';
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
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: TextField(
                controller: _controller,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: 'Enter Stock Ticker',
                ),
              ),
            ),
            ElevatedButton(
              onPressed: () {
                sendStockRequest(_controller.text);
              },
              child: Text('Send Stock Request'),
            ),
            SizedBox(height: 20),
            _response.isNotEmpty
                ? Text(
                    'Response: $_response',
                    style: TextStyle(fontSize: 16),
                  )
                : Container(),
            SizedBox(height: 20),
            _imageUrl.isNotEmpty
                ? Image.network(
                    _imageUrl,
                    errorBuilder: (context, error, stackTrace) {
                      return Text('Failed to load image');
                    },
                  )
                : Container(),
          ],
        ),
      ),
    );
  }
}
