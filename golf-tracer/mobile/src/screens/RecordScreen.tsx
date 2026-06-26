import { CameraView, useCameraPermissions } from 'expo-camera';
import React, { useRef, useState } from 'react';
import {
  Alert,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import { useVideoUpload } from '../hooks/useVideoUpload';
import type { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Record'>;

const FPS_OPTIONS = [60, 120, 240] as const;
type FpsOption = typeof FPS_OPTIONS[number];

export default function RecordScreen({ navigation }: Props) {
  const [permission, requestPermission] = useCameraPermissions();
  const [isRecording, setIsRecording] = useState(false);
  const [selectedFps, setSelectedFps] = useState<FpsOption>(120);
  const cameraRef = useRef<CameraView>(null);
  const { state, upload } = useVideoUpload();

  if (!permission) return <View style={styles.container} />;

  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <Text style={styles.permText}>Camera access required</Text>
        <TouchableOpacity style={styles.btn} onPress={requestPermission}>
          <Text style={styles.btnText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  async function startRecording() {
    if (!cameraRef.current) return;
    setIsRecording(true);
    try {
      const video = await cameraRef.current.recordAsync({
        maxDuration: 30,
      });
      if (video) {
        await handleVideoUri(video.uri);
      }
    } catch (err: any) {
      Alert.alert('Recording error', err.message);
    } finally {
      setIsRecording(false);
    }
  }

  function stopRecording() {
    cameraRef.current?.stopRecording();
    setIsRecording(false);
  }

  async function handleVideoUri(uri: string) {
    const filename = `swing_${Date.now()}.mp4`;
    try {
      const { video, job } = await upload(uri, filename);
      navigation.replace('Processing', { videoId: video.id, jobId: job.id });
    } catch (err: any) {
      Alert.alert('Upload failed', err.message);
    }
  }

  return (
    <View style={styles.container}>
      <CameraView
        ref={cameraRef}
        style={StyleSheet.absoluteFill}
        facing="back"
        mode="video"
        videoQuality="1080p"
      />

      {/* FPS selector */}
      <View style={styles.fpsRow}>
        {FPS_OPTIONS.map((fps) => (
          <TouchableOpacity
            key={fps}
            style={[styles.fpsBtn, fps === selectedFps && styles.fpsBtnActive]}
            onPress={() => setSelectedFps(fps)}
          >
            <Text style={[styles.fpsTxt, fps === selectedFps && styles.fpsTxtActive]}>
              {fps}fps
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Record button */}
      <View style={styles.controls}>
        {state.phase === 'uploading' ? (
          <Text style={styles.uploadTxt}>
            Uploading {Math.round(state.progress * 100)}%
          </Text>
        ) : (
          <TouchableOpacity
            style={[styles.recordBtn, isRecording && styles.recordBtnActive]}
            onPress={isRecording ? stopRecording : startRecording}
          >
            <View style={isRecording ? styles.stopDot : styles.recordDot} />
          </TouchableOpacity>
        )}
      </View>

      <TouchableOpacity style={styles.closeBtn} onPress={() => navigation.goBack()}>
        <Text style={styles.closeTxt}>✕</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  center: { flex: 1, backgroundColor: Colors.background, justifyContent: 'center', alignItems: 'center', gap: 16 },
  permText: { color: Colors.textPrimary, fontSize: 16 },
  btn: { backgroundColor: Colors.primary, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
  btnText: { color: Colors.background, fontWeight: '700' },
  fpsRow: { position: 'absolute', top: 60, right: 20, flexDirection: 'column', gap: 8 },
  fpsBtn: { backgroundColor: 'rgba(0,0,0,0.5)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, borderWidth: 1, borderColor: 'transparent' },
  fpsBtnActive: { borderColor: Colors.accent },
  fpsTxt: { color: Colors.textSecondary, fontSize: 13 },
  fpsTxtActive: { color: Colors.accent },
  controls: { position: 'absolute', bottom: 60, width: '100%', alignItems: 'center' },
  recordBtn: { width: 72, height: 72, borderRadius: 36, backgroundColor: 'transparent', borderWidth: 4, borderColor: '#fff', justifyContent: 'center', alignItems: 'center' },
  recordBtnActive: { borderColor: Colors.error },
  recordDot: { width: 54, height: 54, borderRadius: 27, backgroundColor: Colors.error },
  stopDot: { width: 24, height: 24, borderRadius: 4, backgroundColor: Colors.error },
  uploadTxt: { color: '#fff', fontSize: 18, fontWeight: '600' },
  closeBtn: { position: 'absolute', top: 52, left: 20, width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  closeTxt: { color: '#fff', fontSize: 22 },
});
