import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import React, { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  Slider,
  StyleSheet,
  Switch,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import { triggerExport, getExportStatus, getDownloadUrl } from '../api/export';
import { useTracerConfig } from '../hooks/useTracerConfig';
import { TRACER_PRESETS } from '../constants/tracer';
import type { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Export'>;

type ExportPhase = 'idle' | 'rendering' | 'downloading' | 'done' | 'error';

export default function ExportScreen({ route, navigation }: Props) {
  const { jobId, jobResult, videoUri } = route.params;
  const { config, updateConfig } = useTracerConfig();
  const [phase, setPhase] = useState<ExportPhase>('idle');
  const [exportProgress, setExportProgress] = useState(0);

  async function handleExport() {
    setPhase('rendering');
    try {
      const exportStatus = await triggerExport(jobId, config);

      // Poll for export completion
      let done = false;
      let exportId = exportStatus.id;
      while (!done) {
        await new Promise((r) => setTimeout(r, 2000));
        const status = await getExportStatus(jobId, exportId);
        if (status.status === 'done') {
          done = true;
          setPhase('downloading');
          await downloadAndShare(exportId);
        } else if (status.status === 'error') {
          throw new Error('Export rendering failed');
        }
      }
    } catch (err: any) {
      setPhase('error');
      Alert.alert('Export failed', err.message);
    }
  }

  async function downloadAndShare(exportId: string) {
    const url = getDownloadUrl(exportId);
    const dest = `${FileSystem.documentDirectory}golf-tracer-${exportId.slice(0, 8)}.mp4`;

    const download = FileSystem.createDownloadResumable(url, dest);
    const result = await download.downloadAsync();
    if (!result?.uri) throw new Error('Download failed');

    setPhase('done');
    if (await Sharing.isAvailableAsync()) {
      await Sharing.shareAsync(result.uri, { mimeType: 'video/mp4' });
    } else {
      Alert.alert('Saved', `Video saved to ${result.uri}`);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.sectionTitle}>Tracer Style</Text>

      {/* Presets */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.presets}>
        {Object.entries(TRACER_PRESETS).map(([name, preset]) => (
          <TouchableOpacity
            key={name}
            style={styles.presetChip}
            onPress={() => updateConfig(preset)}
          >
            <View style={[styles.presetDot, { backgroundColor: preset.color }]} />
            <Text style={styles.presetLabel}>{name}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Config sliders */}
      <ConfigSlider
        label={`Thickness: ${config.thickness}px`}
        value={config.thickness}
        min={1}
        max={12}
        step={1}
        onChange={(v) => updateConfig({ thickness: v })}
      />
      <ConfigSlider
        label={`Opacity: ${Math.round(config.opacity * 100)}%`}
        value={config.opacity}
        min={0.1}
        max={1.0}
        step={0.05}
        onChange={(v) => updateConfig({ opacity: v })}
      />
      <ConfigSlider
        label={`Trail Length: ${config.trailLength} frames`}
        value={config.trailLength}
        min={5}
        max={120}
        step={5}
        onChange={(v) => updateConfig({ trailLength: v })}
      />
      <ConfigSlider
        label={`Glow: ${config.glowRadius}px`}
        value={config.glowRadius}
        min={0}
        max={30}
        step={2}
        onChange={(v) => updateConfig({ glowRadius: v })}
      />

      <View style={styles.toggleRow}>
        <Text style={styles.toggleLabel}>Fade tail</Text>
        <Switch
          value={config.fadeTail}
          onValueChange={(v) => updateConfig({ fadeTail: v })}
          trackColor={{ false: Colors.border, true: Colors.accent }}
        />
      </View>

      {/* Export button */}
      <TouchableOpacity
        style={[styles.exportBtn, phase !== 'idle' && { opacity: 0.7 }]}
        onPress={handleExport}
        disabled={phase !== 'idle' && phase !== 'error'}
      >
        {phase === 'rendering' || phase === 'downloading' ? (
          <ActivityIndicator color={Colors.background} />
        ) : (
          <Text style={styles.exportBtnTxt}>
            {phase === 'done' ? 'Shared!' : 'Export & Share'}
          </Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

function ConfigSlider({ label, value, min, max, step, onChange }: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
}) {
  return (
    <View style={sliderStyles.row}>
      <Text style={sliderStyles.label}>{label}</Text>
      <Slider
        style={sliderStyles.slider}
        value={value}
        minimumValue={min}
        maximumValue={max}
        step={step}
        onValueChange={onChange}
        minimumTrackTintColor={Colors.accent}
        maximumTrackTintColor={Colors.border}
        thumbTintColor={Colors.accent}
      />
    </View>
  );
}

const sliderStyles = StyleSheet.create({
  row: { marginBottom: 16 },
  label: { color: Colors.textSecondary, fontSize: 13, marginBottom: 4 },
  slider: { height: 36 },
});

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { padding: 20, gap: 4 },
  sectionTitle: { color: Colors.textPrimary, fontSize: 18, fontWeight: '700', marginBottom: 12 },
  presets: { marginBottom: 20 },
  presetChip: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: Colors.surfaceElevated, borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, marginRight: 10 },
  presetDot: { width: 12, height: 12, borderRadius: 6 },
  presetLabel: { color: Colors.textPrimary, fontSize: 13 },
  toggleRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 12 },
  toggleLabel: { color: Colors.textSecondary, fontSize: 15 },
  exportBtn: { backgroundColor: Colors.primary, padding: 18, borderRadius: 14, alignItems: 'center', marginTop: 24 },
  exportBtnTxt: { color: Colors.background, fontSize: 18, fontWeight: '700' },
});
