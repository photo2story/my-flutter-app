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
  List<String> _reviewedTickers = [];
  final TextEditingController _controller = TextEditingController();

  // 환경 변수 직접 포함
  final String apiUrl = 'http://localhost:5000/api/get_reviewed_tickers';
  final String fetchImagesApiUrl = 'https://api.github.com/repos/photo2story/my-flutter-app/contents/static/images';
  final String flaskApiUrl = 'http://localhost:5000/execute_stock_command';

  @override
  void initState() {
    super.initState();
    fetchReviewedTickers();
  }

  Future<void> fetchReviewedTickers() async {
    try {
      final response = await http.get(Uri.parse(apiUrl));
      if (response.statusCode == 200) {
        final List<dynamic> tickers = json.decode(response.body);
        setState(() {
          _reviewedTickers = tickers.cast<String


// flutter devices

// flutter run -d R3CX404VPHE

// flutter run -d chrome