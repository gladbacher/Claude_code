import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import type { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Home'>;

export default function HomeScreen({ navigation }: Props) {
  return (
    <View style={styles.container}>
      <View style={styles.hero}>
        <Text style={styles.logo}>⛳ GolfTracer</Text>
        <Text style={styles.tagline}>Automatic ball tracing for your swing</Text>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.btn, styles.btnPrimary]}
          onPress={() => navigation.navigate('Record')}
        >
          <Text style={styles.btnTextPrimary}>Record Swing</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.btn, styles.btnSecondary]}
          onPress={() => navigation.navigate('Import')}
        >
          <Text style={styles.btnTextSecondary}>Import Video</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.features}>
        <Text style={styles.featuresTitle}>Features</Text>
        {FEATURES.map((f) => (
          <View key={f} style={styles.featureRow}>
            <Text style={styles.featureDot}>▸</Text>
            <Text style={styles.featureText}>{f}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const FEATURES = [
  'Automatic golf ball detection',
  'Impact frame detection',
  'Smooth ball flight tracer',
  'Customisable tracer style',
  'Manual correction tools',
  'Export in 1080p',
];

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background, padding: 24 },
  hero: { alignItems: 'center', marginTop: 40, marginBottom: 40 },
  logo: { color: Colors.primary, fontSize: 36, fontWeight: 'bold' },
  tagline: { color: Colors.textSecondary, fontSize: 16, marginTop: 8, textAlign: 'center' },
  actions: { gap: 14, marginBottom: 40 },
  btn: {
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
  },
  btnPrimary: { backgroundColor: Colors.primary },
  btnSecondary: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
    borderColor: Colors.primary,
  },
  btnTextPrimary: { color: Colors.background, fontSize: 18, fontWeight: '700' },
  btnTextSecondary: { color: Colors.primary, fontSize: 18, fontWeight: '600' },
  features: { gap: 8 },
  featuresTitle: { color: Colors.textSecondary, fontSize: 14, marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 },
  featureRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  featureDot: { color: Colors.accent, fontSize: 12 },
  featureText: { color: Colors.textPrimary, fontSize: 15 },
});
