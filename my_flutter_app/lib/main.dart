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
  String _message = '';
  final TextEditingController _controller = TextEditingController();

  final String executeCommandApiUrl = 'http://192.168.0.5:5000/execute_stock_command';

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
          _message = 'Command execution failed: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _message = 'An error occurred: $e';
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
                  onSubmitted: (value) {
                    executeStockCommand(_controller.text.toUpperCase());
                  },
                ),
              ),
              ElevatedButton(
                onPressed: () {
                  executeStockCommand(_controller.text.toUpperCase());
                },
                child: Text('Test Stock'),
              ),
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

// flutter devices

// flutter run -d R3CX404VPHE

// flutter run -d chrome