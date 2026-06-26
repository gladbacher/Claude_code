import React, { useEffect } from 'react';
import {
  ActivityIndicator,
  Alert,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import { useJobPolling } from '../hooks/useJobPolling';
import { getJobResult } from '../api/jobs';
import type { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Processing'>;

export default function ProcessingScreen({ route, navigation }: Props) {
  const { jobId, videoId } = route.params;
  const { status, result, error } = useJobPolling(jobId);

  useEffect(() => {
    if (result) {
      // Navigate to result with a placeholder video URI
      // In production, this would be the original uploaded video URI
      navigation.replace('Result', {
        videoUri: `http://10.0.2.2:8000/videos/${videoId}`,
        jobResult: result,
        jobId,
      });
    }
  }, [result, navigation, jobId, videoId]);

  useEffect(() => {
    if (error) {
      Alert.alert('Processing failed', error, [
        { text: 'OK', onPress: () => navigation.navigate('Home') },
      ]);
    }
  }, [error, navigation]);

  const progressPercent = Math.round((status?.progress ?? 0) * 100);
  const message = status?.progress_message ?? 'Starting…';

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Analysing Swing</Text>

      <View style={styles.progressWrap}>
        <View style={styles.progressTrack}>
          <View style={[styles.progressBar, { width: `${progressPercent}%` as any }]} />
        </View>
        <Text style={styles.progressText}>{progressPercent}%</Text>
      </View>

      <Text style={styles.message}>{message}</Text>

      <ActivityIndicator
        size="large"
        color={Colors.accent}
        style={{ marginTop: 32 }}
      />

      <Text style={styles.hint}>
        The AI is detecting your golf ball and tracing its flight path…
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background, justifyContent: 'center', alignItems: 'center', padding: 32, gap: 16 },
  title: { color: Colors.textPrimary, fontSize: 24, fontWeight: 'bold', marginBottom: 8 },
  progressWrap: { width: '100%', alignItems: 'center', gap: 8 },
  progressTrack: { width: '100%', height: 6, backgroundColor: Colors.surfaceElevated, borderRadius: 3, overflow: 'hidden' },
  progressBar: { height: '100%', backgroundColor: Colors.accent, borderRadius: 3 },
  progressText: { color: Colors.accent, fontSize: 18, fontWeight: '700' },
  message: { color: Colors.textSecondary, fontSize: 14, textAlign: 'center' },
  hint: { color: Colors.textMuted, fontSize: 12, textAlign: 'center', marginTop: 16, maxWidth: 280 },
});
