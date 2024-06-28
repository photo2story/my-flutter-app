import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future<void> main() async {
  await dotenv.load(fileName: ".env");
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);
  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  bool _isLoading = false;
  String _message = '';

  Future<void> sendPingCommand() async {
    setState(() {
      _isLoading = true;
      _message = '';
    });

    try {
      final url = Uri.parse('http://${dotenv.env['FLASK_SERVER_HOST']}/execute_discord_command');
      final response = await http.post(
        url,
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
        },
        body: jsonEncode(<String, String>{
          'command': 'ping',
        }),
      );

      if (response.statusCode == 200) {
        setState(() {
          _message = 'Message sent to Discord: ping';
        });
      } else {
        setState(() {
          _message = 'Failed to send message to Discord.';
        });
      }
    } catch (e) {
      setState(() {
        _message = 'Error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'Press the button to send a message to Discord:',
            ),
            if (_isLoading)
              CircularProgressIndicator()
            else
              Text(
                _message,
                style: TextStyle(color: _message.contains('Failed') ? Colors.red : Colors.green),
              ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: sendPingCommand,
        tooltip: 'Send Ping',
        child: Icon(Icons.send),
      ),
    );
  }
}
