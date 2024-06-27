import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:discord_logger/discord_logger.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // .env 파일을 로드
  await dotenv.load(fileName: 'assets/.env');

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
  void _sendDiscordMessage() async {
    final discord = DiscordLogger.instance;
    debugPrint('Sending message to Discord...'); // 디버그 로그 추가
    try {
      await discord.sendMessage("This is a test message from Flutter");
      debugPrint('Message sent successfully!');
    } catch (e) {
      debugPrint('Error sending message: $e');
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
            const Text(
              'Press the button to send a message to Discord:',
            ),
            SizedBox(height: 20),
            FloatingActionButton(
              onPressed: _sendDiscordMessage,
              tooltip: 'Send Message',
              child: const Icon(Icons.send),
            ),
          ],
        ),
      ),
    );
  }
}
