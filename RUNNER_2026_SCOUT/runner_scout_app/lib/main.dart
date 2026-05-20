import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'firebase_options.dart';

// --- CONSTANTES DE COLOR ---
const Color primaryDark = Color(0xFF093129);
const Color accentYellow = Color(0xFFFFC107);
const Color accentPurple = Color(0xFFB388FF);
const Color bgLight = Color(0xFFF5F7F9);

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  runApp(const RunnerScoutApp());
}

class RunnerScoutApp extends StatelessWidget {
  const RunnerScoutApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Runner Scout 2026',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: primaryDark),
        useMaterial3: true,
        fontFamily: 'Poppins',
      ),
      home: const LoginScreen(),
    );
  }
}

// --- PANTALLA DE LOGIN ---
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _cedulaController = TextEditingController();
  bool _isLoading = false;

  Future<void> _login() async {
    setState(() => _isLoading = true);
    try {
      var userDoc = await FirebaseFirestore.instance
          .collection('participantes')
          .doc(_cedulaController.text.trim())
          .get();

      if (userDoc.exists) {
        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => HomeRouter(
              userData: userDoc.data()!,
              cedula: _cedulaController.text.trim(),
            ),
          ),
        );
      } else {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text("Cédula no registrada")));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: primaryDark,
      body: Padding(
        padding: const EdgeInsets.all(30),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.terrain, size: 80, color: accentYellow),
            const Text(
              "RUN SCOUTS 2026",
              style: TextStyle(
                color: Colors.white,
                fontSize: 26,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 40),
            TextField(
              controller: _cedulaController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.white,
                labelText: "Cédula de Identidad",
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
              ),
            ),
            const SizedBox(height: 20),
            _isLoading
                ? const CircularProgressIndicator(color: accentYellow)
                : ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: accentYellow,
                      minimumSize: const Size(double.infinity, 50),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                    ),
                    onPressed: _login,
                    child: const Text(
                      "ENTRAR",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: primaryDark,
                      ),
                    ),
                  ),
          ],
        ),
      ),
    );
  }
}

// --- ROUTER PRINCIPAL ---
class HomeRouter extends StatefulWidget {
  final Map<String, dynamic> userData;
  final String cedula;
  const HomeRouter({super.key, required this.userData, required this.cedula});

  @override
  State<HomeRouter> createState() => _HomeRouterState();
}

class _HomeRouterState extends State<HomeRouter> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    bool isCorredor = widget.userData['rol'] == 'corredor';

    final List<Widget> pages = [
      UserTab(userData: widget.userData, cedula: widget.cedula),
      MyGroupTab(userData: widget.userData),
      const Route8kTab(),
      isCorredor ? const ScoreTab() : const EvaluationTab(),
      const ScoreboardTab(),
    ];

    return Scaffold(
      backgroundColor: bgLight,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          "RUN SCOUTS 2026",
          style: TextStyle(
            fontSize: 18,
            color: primaryDark,
            fontWeight: FontWeight.w900,
            letterSpacing: 1.2,
          ),
        ),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.menu, color: primaryDark),
          onPressed: () {},
        ),
      ),
      body: pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.white,
        selectedItemColor: primaryDark,
        unselectedItemColor: Colors.grey[400],
        items: [
          _buildNavItem(Icons.person, "USER", 0),
          _buildNavItem(Icons.groups, "MY GROUP", 1),
          _buildNavItem(Icons.route, "ROUTE 8K", 2),
          _buildNavItem(
            Icons.assignment_turned_in,
            isCorredor ? "SCORE" : "EVAL",
            3,
          ),
          _buildNavItem(Icons.leaderboard, "SCOREBOARD", 4),
        ],
      ),
    );
  }

  BottomNavigationBarItem _buildNavItem(
    IconData icon,
    String label,
    int index,
  ) {
    return BottomNavigationBarItem(
      icon: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: _selectedIndex == index ? accentYellow : Colors.transparent,
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon),
      ),
      label: label,
    );
  }
}

// --- PESTAÑA 0: USER (FIX DEFINITIVO DE TICKETS VISIBLES) ---
class UserTab extends StatelessWidget {
  final Map<String, dynamic> userData;
  final String cedula;
  const UserTab({super.key, required this.userData, required this.cedula});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<DocumentSnapshot>(
      stream: FirebaseFirestore.instance
          .collection('participantes')
          .doc(cedula)
          .snapshots(),
      builder: (context, snapshot) {
        if (!snapshot.hasData)
          return const Center(child: CircularProgressIndicator());

        var currentData = snapshot.data!.data() as Map<String, dynamic>? ?? {};

        // Conversión segura de los tickets
        Map<String, dynamic> tickets = {};
        if (currentData['tickets'] != null && currentData['tickets'] is Map) {
          tickets = Map<String, dynamic>.from(currentData['tickets']);
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // --- Perfil ---
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.grey[200]!),
                ),
                child: Row(
                  children: [
                    const CircleAvatar(
                      radius: 35,
                      backgroundColor: primaryDark,
                      child: Icon(Icons.person, color: Colors.white, size: 40),
                    ),
                    const SizedBox(width: 15),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          (currentData['rol'] ?? 'CORREDOR').toUpperCase(),
                          style: const TextStyle(
                            color: accentPurple,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                        Text(
                          currentData['nombre_completo'] ?? 'Nombre',
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w900,
                            color: primaryDark,
                          ),
                        ),
                        const SizedBox(height: 5),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: bgLight,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Row(
                            children: [
                              const Icon(
                                Icons.people,
                                size: 14,
                                color: Colors.grey,
                              ),
                              const SizedBox(width: 5),
                              Text(
                                "Equipo ${currentData['equipo_id'] ?? 'N/A'}",
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 25),

              // --- QR Credencial ---
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.grey[200]!),
                ),
                child: Column(
                  children: [
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          "Credencial Digital",
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w900,
                            color: primaryDark,
                          ),
                        ),
                        Icon(Icons.qr_code_scanner, color: accentPurple),
                      ],
                    ),
                    const SizedBox(height: 20),
                    Container(
                      padding: const EdgeInsets.all(15),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E1E1E),
                        borderRadius: BorderRadius.circular(15),
                      ),
                      child: Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: accentYellow,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: QrImageView(
                          data: "USER:$cedula",
                          size: 140,
                          backgroundColor: accentYellow,
                        ),
                      ),
                    ),
                    const SizedBox(height: 15),
                    const Text(
                      "Muestra este código al staff en las\nestaciones para registrar tu actividad.",
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
              ),

              // --- LÓGICA DINÁMICA DE TICKETS ---
              if (tickets.isNotEmpty) ...[
                const SizedBox(height: 30),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(5),
                      decoration: BoxDecoration(
                        color: primaryDark,
                        borderRadius: BorderRadius.circular(5),
                      ),
                      child: const Icon(
                        Icons.local_activity,
                        color: Colors.white,
                        size: 16,
                      ),
                    ),
                    const SizedBox(width: 10),
                    const Text(
                      "Mis Tickets",
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                        color: primaryDark,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 15),
                // Aquí llamamos a la función segura
                ...tickets.entries.map((entry) {
                  return _buildSafeTicketCard(
                    entry.key.toString(),
                    entry.value.toString(),
                  );
                }).toList(),
              ],
            ],
          ),
        );
      },
    );
  }

  // --- TARJETA A PRUEBA DE FALLOS DE FLUTTER ---
  Widget _buildSafeTicketCard(String type, String value) {
    IconData icon = Icons.star;
    Color color = Colors.grey;
    String subtitle = "Actividad Scout";
    String info = value;

    String safeType = type.trim().toLowerCase();

    if (safeType == 'concierto') {
      icon = Icons.music_note;
      color = accentPurple;
      subtitle = "Escenario Principal";
      info = "$value Entrada(s)";
    } else if (safeType == 'tirolina') {
      icon = Icons.downhill_skiing;
      color = primaryDark;
      subtitle = "Zona Bosque Alto";
      info = "$value Turnos";
    } else if (safeType == 'comida') {
      icon = Icons.restaurant;
      color = Colors.orange;
      subtitle = "Área de Comedor";
      info = "$value Raciones";
    } else if (safeType.contains('trampol')) {
      icon = Icons.sports_gymnastics;
      color = Colors.brown;
      subtitle = "Área de Juegos";
      info = "Ilimitado";
    }

    String displayTitle = safeType.isNotEmpty
        ? safeType[0].toUpperCase() + safeType.substring(1)
        : "Ticket";

    return Card(
      margin: const EdgeInsets.only(bottom: 15),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
        side: BorderSide(color: Colors.grey[200]!, width: 1),
      ),
      clipBehavior: Clip.antiAlias,
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Franja de color a la izquierda
            Container(width: 6, color: color),

            // Contenido real de la tarjeta
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(15.0),
                child: Row(
                  children: [
                    CircleAvatar(
                      backgroundColor: color.withOpacity(0.1),
                      child: Icon(icon, color: color),
                    ),
                    const SizedBox(width: 15),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            displayTitle,
                            style: const TextStyle(
                              fontWeight: FontWeight.w900,
                              color: primaryDark,
                              fontSize: 18,
                            ),
                          ),
                          Text(
                            subtitle,
                            style: const TextStyle(
                              color: Colors.grey,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: bgLight,
                        borderRadius: BorderRadius.circular(15),
                      ),
                      child: Text(
                        info,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                          color: primaryDark,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// --- PESTAÑA 1: MY GROUP (DATOS REALES) ---
class MyGroupTab extends StatelessWidget {
  final Map<String, dynamic> userData;
  const MyGroupTab({super.key, required this.userData});

  Future<Map<String, dynamic>> _fetchGroupData() async {
    String equipoId = userData['equipo_id'];
    var equipoDoc = await FirebaseFirestore.instance
        .collection('equipos')
        .doc(equipoId)
        .get();
    var participantesQuery = await FirebaseFirestore.instance
        .collection('participantes')
        .where('equipo_id', isEqualTo: equipoId)
        .get();

    return {
      'equipo': equipoDoc.exists ? equipoDoc.data() : null,
      'miembros': participantesQuery.docs.map((e) => e.data()).toList(),
    };
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: _fetchGroupData(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(
            child: CircularProgressIndicator(color: primaryDark),
          );
        }

        if (snapshot.hasError || !snapshot.hasData) {
          return const Center(
            child: Text("Error al cargar los datos del equipo"),
          );
        }

        var data = snapshot.data!;
        var equipoData = data['equipo'] as Map<String, dynamic>? ?? {};
        var miembros = data['miembros'] as List<Map<String, dynamic>>;

        String nombreGrupo =
            equipoData['nombre_grupo'] ?? userData['equipo_id'];

        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.grey[200]!),
                ),
                child: Column(
                  children: [
                    const CircleAvatar(
                      radius: 35,
                      backgroundColor: primaryDark,
                      child: Icon(Icons.gite, color: Colors.white, size: 35),
                    ),
                    const SizedBox(height: 15),
                    Text(
                      nombreGrupo,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w900,
                        color: primaryDark,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 25),
                    Container(
                      padding: const EdgeInsets.all(15),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(15),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.05),
                            blurRadius: 10,
                            spreadRadius: 2,
                          ),
                        ],
                      ),
                      child: QrImageView(
                        data: "EQUIPO:${userData['equipo_id']}",
                        size: 160,
                        foregroundColor: primaryDark,
                      ),
                    ),
                    const SizedBox(height: 10),
                    const Text(
                      "QR Oficial del Equipo",
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 30),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    "Integrantes",
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w900,
                      color: primaryDark,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 5,
                    ),
                    decoration: BoxDecoration(
                      color: accentPurple.withOpacity(0.5),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      "${miembros.length} Miembros",
                      style: const TextStyle(
                        color: primaryDark,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 15),
              ...miembros.map((miembro) {
                bool isLeader =
                    miembro['rol'].toString().toLowerCase() == 'guia' ||
                    miembro['rol'].toString().toLowerCase() == 'guía';

                return _buildMemberCard(
                  miembro['nombre_completo'] ?? 'Sin Nombre',
                  (miembro['rol'] ?? 'Corredor').toString().toUpperCase(),
                  isLeader ? Icons.star : Icons.person,
                  isLeader,
                );
              }).toList(),
            ],
          ),
        );
      },
    );
  }

  Widget _buildMemberCard(
    String name,
    String role,
    IconData icon,
    bool isLeader,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 15),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        children: [
          Container(
            height: 100,
            decoration: const BoxDecoration(
              color: bgLight,
              borderRadius: BorderRadius.vertical(top: Radius.circular(15)),
            ),
            child: const Center(
              child: Icon(Icons.image, color: Colors.grey, size: 40),
            ),
          ),
          Transform.translate(
            offset: const Offset(0, -20),
            child: CircleAvatar(
              radius: 20,
              backgroundColor: isLeader ? primaryDark : Colors.grey[300],
              child: Icon(
                icon,
                color: isLeader ? Colors.white : primaryDark,
                size: 20,
              ),
            ),
          ),
          Transform.translate(
            offset: const Offset(0, -10),
            child: Column(
              children: [
                Text(
                  name,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w900,
                    color: primaryDark,
                  ),
                ),
                Text(
                  role,
                  style: TextStyle(
                    color: isLeader ? accentPurple : primaryDark,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// --- PESTAÑA 2: ROUTE 8K ---
class Route8kTab extends StatelessWidget {
  const Route8kTab({super.key});
  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.map, size: 80, color: Colors.blue),
          Text(
            "Mapa de Ruta 8K",
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          Text("Próximamente disponible..."),
        ],
      ),
    );
  }
}

// --- PESTAÑA 3 (Staff): EVALUATION ---
class EvaluationTab extends StatelessWidget {
  const EvaluationTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: MobileScanner(
        onDetect: (capture) {
          final List<Barcode> barcodes = capture.barcodes;
          for (final barcode in barcodes) {
            final String code = barcode.rawValue ?? "";
            if (code.isNotEmpty) {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text("QR Escaneado"),
                  content: Text("ID Detectado: $code"),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text("Cerrar"),
                    ),
                  ],
                ),
              );
              break;
            }
          }
        },
      ),
    );
  }
}

// --- PESTAÑA 3 (Corredores): SCORE ---
class ScoreTab extends StatelessWidget {
  const ScoreTab({super.key});
  @override
  Widget build(BuildContext context) {
    return const Center(child: Text("Historial de Postas (Score UI)"));
  }
}

// --- PESTAÑA 4: SCOREBOARD ---
class ScoreboardTab extends StatelessWidget {
  const ScoreboardTab({super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<QuerySnapshot>(
      stream: FirebaseFirestore.instance
          .collection('equipos')
          .orderBy('puntos_totales', descending: true)
          .snapshots(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(
            child: CircularProgressIndicator(color: primaryDark),
          );
        }

        if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
          return const Center(child: Text("Aún no hay puntajes registrados."));
        }

        var equipos = snapshot.data!.docs;

        return ListView.builder(
          padding: const EdgeInsets.all(15),
          itemCount: equipos.length,
          itemBuilder: (context, index) {
            var equipo = equipos[index];
            bool isFirst = index == 0;

            return Card(
              elevation: isFirst ? 4 : 1,
              margin: const EdgeInsets.only(bottom: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
                side: isFirst
                    ? const BorderSide(color: accentYellow, width: 2)
                    : BorderSide.none,
              ),
              child: ListTile(
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 10,
                ),
                leading: CircleAvatar(
                  radius: 20,
                  backgroundColor: isFirst ? accentYellow : primaryDark,
                  foregroundColor: isFirst ? primaryDark : Colors.white,
                  child: Text(
                    "${index + 1}",
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ),
                title: Text(
                  equipo['nombre_grupo'] ?? 'Equipo ${equipo.id}',
                  style: const TextStyle(
                    fontWeight: FontWeight.w900,
                    color: primaryDark,
                    fontSize: 18,
                  ),
                ),
                subtitle: Text(
                  "ID: ${equipo.id}",
                  style: const TextStyle(color: Colors.grey),
                ),
                trailing: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: isFirst
                        ? accentYellow.withOpacity(0.2)
                        : Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    "${equipo['puntos_totales'] ?? 0} pts",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: isFirst ? primaryDark : Colors.green[700],
                      fontSize: 16,
                    ),
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }
}
