import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:google_fonts/google_fonts.dart';

// Este archivo es el que vincula tu app con la nube de Google
import 'firebase_options.dart'; 

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const AppConciertoScout());
}

class AppConciertoScout extends StatelessWidget {
  const AppConciertoScout({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Acceso Concierto Scout',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF093129)),
        textTheme: GoogleFonts.poppinsTextTheme(),
        useMaterial3: true,
      ),
      home: const PantallaLogin(),
    );
  }
}

class PantallaLogin extends StatefulWidget {
  const PantallaLogin({super.key});

  @override
  State<PantallaLogin> createState() => _PantallaLoginState();
}

class _PantallaLoginState extends State<PantallaLogin> {
  final TextEditingController _cedulaController = TextEditingController();
  bool _cargando = false;

  Future<void> _entrar() async {
    final ci = _cedulaController.text.trim();
    if (ci.isEmpty) return;

    setState(() => _cargando = true);

    try {
      final doc = await FirebaseFirestore.instance
          .collection('participantes')
          .doc(ci)
          .get();

      if (!mounted) return;

      if (doc.exists) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => PantallaTicket(datos: doc.data()!, cedula: ci),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Cédula no registrada")),
        );
      }
    } finally {
      if (mounted) setState(() => _cargando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(30.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.festival, size: 80, color: Color(0xFF093129)),
            const SizedBox(height: 10),
            const Text("Acceso Concierto", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 40),
            TextField(
              controller: _cedulaController,
              decoration: const InputDecoration(
                labelText: "Tu Cédula",
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.person),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: _cargando ? null : _entrar,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF093129),
                  foregroundColor: Colors.white,
                ),
                child: _cargando ? const CircularProgressIndicator(color: Colors.white) : const Text("BUSCAR ENTRADA"),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class PantallaTicket extends StatelessWidget {
  final Map<String, dynamic> datos;
  final String cedula;
  const PantallaTicket({super.key, required this.datos, required this.cedula});

  @override
  Widget build(BuildContext context) {
    bool usada = datos['entrada_usada'] ?? false;

    return Scaffold(
      appBar: AppBar(title: const Text("Mi QR de Entrada")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(datos['nombre_completo'] ?? "Participante", style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            Text("Grupo: ${datos['grupo_scout'] ?? 'N/A'}", style: const TextStyle(fontSize: 16, color: Colors.grey)),
            const SizedBox(height: 30),
            if (usada)
              const Column(
                children: [
                  Icon(Icons.block, color: Colors.red, size: 100),
                  Text("ESTA ENTRADA YA FUE USADA", style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                ],
              )
            else
              QrImageView(data: cedula, size: 280),
          ],
        ),
      ),
    );
  }
}