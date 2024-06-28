import 'package:flutter/material.dart';

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

  void updateImageUrl(String stockName) {
    setState(() {
      _imageUrl = 'https://github.com/photo2story/my-flutter-app/blob/main/my-flask-app/comparison_${stockName.toUpperCase()}_VOO.png?raw=true';
      _message = '';
    });
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
                textCapitalization: TextCapitalization.characters,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: 'Enter Stock Ticker',
                ),
              ),
            ),
            ElevatedButton(
              onPressed: () {
                updateImageUrl(_controller.text);
              },
              child: Text('Get Stock Image'),
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
    );
  }
}
