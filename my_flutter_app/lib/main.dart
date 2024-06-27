import 'package:flutter/material.dart';
import 'package:dotenv/dotenv.dart' as dotenv;
import 'package:discord_logger/discord_logger.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  dotenv.load();  // .env 파일 로드
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // 환경 변수에서 Discord 자격 증명 로드
    final channelId = dotenv.env['DISCORD_CHANNEL_ID'] ?? '';
    final botToken = dotenv.env['DISCORD_APPLICATION_TOKEN'] ?? '';

    // DiscordLogger 초기화
    DiscordLogger(
      channelId: channelId,
      botToken: botToken,
    );

    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  void _sendDiscordMessage() {
    final discord = DiscordLogger.instance;
    discord.sendMessage("This is a test message from Flutter");
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
            const Text(
              'Press the button to send a message to Discord:',
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _sendDiscordMessage,
        tooltip: 'Send Message',
        child: const Icon(Icons.send),
      ),
    );
  }
}
