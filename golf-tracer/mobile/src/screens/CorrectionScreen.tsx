import React, { useState } from 'react';
import {
  Alert,
  Dimensions,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import { useFrameCorrections } from '../hooks/useFrameCorrections';
import { getFrameUrl } from '../api/jobs';
import { API_BASE_URL } from '../constants/api';
import type { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Correction'>;

const { width: SCREEN_W } = Dimensions.get('window');

export default function CorrectionScreen({ route, navigation }: Props) {
  const { jobId, jobResult, videoUri } = route.params;
  const [currentFrame, setCurrentFrame] = useState(jobResult.impact_frame);
  const { addCorrection, deleteCorrection, pendingCount, saving, commitCorrections } =
    useFrameCorrections(jobId);

  const frameUrl = `${API_BASE_URL}/jobs/${jobId}/frames/${currentFrame}`;

  async function handleSave() {
    const result = await commitCorrections();
    if (result) {
      Alert.alert('Saved', `${pendingCount} corrections applied.`, [
        {
          text: 'View Result',
          onPress: () =>
            navigation.replace('Result', { videoUri, jobResult: result, jobId }),
        },
      ]);
    }
  }

  function handleTap(evt: any) {
    const { locationX, locationY } = evt.nativeEvent;
    const x = locationX / SCREEN_W;
    const y = locationY / (SCREEN_W / (jobResult.width / jobResult.height));
    addCorrection(currentFrame, x, y);
  }

  const totalFrames = jobResult.frame_count;
  const thumbFrames = Array.from({ length: Math.min(totalFrames, 60) }, (_, i) =>
    Math.floor((i / 60) * totalFrames)
  );

  return (
    <View style={styles.container}>
      {/* Frame preview */}
      <TouchableOpacity activeOpacity={0.9} onPress={handleTap} style={styles.frameWrap}>
        <Image source={{ uri: frameUrl }} style={styles.frameImage} resizeMode="contain" />
        <Text style={styles.frameLabel}>Frame {currentFrame} — Tap to place ball</Text>
      </TouchableOpacity>

      {/* Frame scrubber */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrubber}>
        {thumbFrames.map((frame) => (
          <TouchableOpacity
            key={frame}
            style={[styles.thumb, frame === currentFrame && styles.thumbActive]}
            onPress={() => setCurrentFrame(frame)}
          >
            <Text style={styles.thumbLabel}>{frame}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.deleteBtn}
          onPress={() => deleteCorrection(currentFrame)}
        >
          <Text style={styles.deleteTxt}>Delete Point</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.saveBtn, saving && { opacity: 0.6 }]}
          onPress={handleSave}
          disabled={saving || pendingCount === 0}
        >
          <Text style={styles.saveTxt}>
            {saving ? 'Saving…' : `Save ${pendingCount} Corrections`}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  frameWrap: { backgroundColor: '#000', alignItems: 'center' },
  frameImage: { width: SCREEN_W, height: (SCREEN_W * 9) / 16 },
  frameLabel: { color: Colors.textMuted, fontSize: 12, padding: 4 },
  scrubber: { maxHeight: 60, paddingVertical: 8, paddingHorizontal: 12 },
  thumb: {
    width: 50,
    height: 40,
    backgroundColor: Colors.surfaceElevated,
    marginRight: 6,
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: 'transparent',
  },
  thumbActive: { borderColor: Colors.accent },
  thumbLabel: { color: Colors.textSecondary, fontSize: 10 },
  actions: { padding: 16, gap: 12, flexDirection: 'row' },
  deleteBtn: { flex: 1, backgroundColor: Colors.surfaceElevated, padding: 14, borderRadius: 10, alignItems: 'center' },
  deleteTxt: { color: Colors.error, fontWeight: '600' },
  saveBtn: { flex: 2, backgroundColor: Colors.primary, padding: 14, borderRadius: 10, alignItems: 'center' },
  saveTxt: { color: Colors.background, fontWeight: '700' },
});
