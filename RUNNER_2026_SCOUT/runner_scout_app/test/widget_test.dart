import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:runner_scout_app/main.dart';

void main() {
  testWidgets('Verificar pantalla de login de RunnerScout', (
    WidgetTester tester,
  ) async {
    // Cargamos la aplicación
    await tester.pumpWidget(const RunnerScoutApp());

    // Verificamos que aparezca el título de la app y el botón de entrar
    expect(find.text('RUN SCOUTS 2026'), findsOneWidget);
    expect(find.text('ENTRAR'), findsOneWidget);

    // Verificamos que el campo de Cédula esté presente
    expect(find.byType(TextField), findsOneWidget);
  });
}
