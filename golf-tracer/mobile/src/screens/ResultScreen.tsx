import { useVideoPlayer, VideoView } from 'expo-video';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Dimensions,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import TracerOverlay from '../components/TracerOverlay';
import { useTracerConfig } from '../hooks/useTracerConfig';
import type { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Result'>;

const { width: SCREEN_W, height: SCREEN_H } = Dimensions.get('window');

export default function ResultScreen({ route, navigation }: Props) {
  const { videoUri, jobResult, jobId } = route.params;
  const { config } = useTracerConfig();
  const [currentFrame, setCurrentFrame] = useState(jobResult.impact_frame);

  const player = useVideoPlayer(videoUri, (p) => {
    p.loop = true;
  });

  // Sync frame index from playback time
  useEffect(() => {
    const interval = setInterval(() => {
      if (player && jobResult.fps > 0) {
        const frame = Math.floor(player.currentTime * jobResult.fps);
        setCurrentFrame(frame);
      }
    }, 50); // ~20fps update rate for overlay
    return () => clearInterval(interval);
  }, [player, jobResult.fps]);

  const videoAspect = jobResult.width / Math.max(jobResult.height, 1);
  const containerWidth = SCREEN_W;
  const containerHeight = containerWidth / videoAspect;

  return (
    <View style={styles.container}>
      {/* Video + tracer overlay */}
      <View style={[styles.videoWrap, { height: containerHeight }]}>
        <VideoView
          style={StyleSheet.absoluteFill}
          player={player}
          allowsFullscreen={false}
          allowsPictureInPicture={false}
          contentFit="contain"
        />
        <TracerOverlay
          trackingPoints={jobResult.tracking_points}
          currentFrame={currentFrame}
          videoWidth={jobResult.width}
          videoHeight={jobResult.height}
          containerWidth={containerWidth}
          containerHeight={containerHeight}
          config={config}
        />
      </View>

      {/* Stats */}
      <View style={styles.stats}>
        <StatPill label="Impact" value={`Frame ${jobResult.impact_frame}`} />
        <StatPill label="FPS" value={`${Math.round(jobResult.fps)}`} />
        <StatPill label="Coverage" value={`${Math.round(jobResult.coverage * 100)}%`} />
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.btnSecondary}
          onPress={() => navigation.navigate('Correction', { jobId, jobResult, videoUri })}
        >
          <Text style={styles.btnTextSecondary}>Manual Corrections</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.btnPrimary}
          onPress={() => navigation.navigate('Export', { jobId, jobResult, videoUri })}
        >
          <Text style={styles.btnTextPrimary}>Export Video</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

function StatPill({ label, value }: { label: string; value: string }) {
  return (
    <View style={statStyles.pill}>
      <Text style={statStyles.label}>{label}</Text>
      <Text style={statStyles.value}>{value}</Text>
    </View>
  );
}

const statStyles = StyleSheet.create({
  pill: { backgroundColor: Colors.surfaceElevated, borderRadius: 10, paddingHorizontal: 16, paddingVertical: 10, alignItems: 'center' },
  label: { color: Colors.textMuted, fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.5 },
  value: { color: Colors.textPrimary, fontSize: 16, fontWeight: '700' },
});

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  videoWrap: { width: SCREEN_W, position: 'relative', backgroundColor: '#000' },
  stats: { flexDirection: 'row', justifyContent: 'space-evenly', padding: 16 },
  actions: { padding: 16, gap: 12 },
  btnPrimary: { backgroundColor: Colors.primary, padding: 16, borderRadius: 12, alignItems: 'center' },
  btnSecondary: { backgroundColor: Colors.surfaceElevated, padding: 16, borderRadius: 12, alignItems: 'center' },
  btnTextPrimary: { color: Colors.background, fontSize: 16, fontWeight: '700' },
  btnTextSecondary: { color: Colors.textPrimary, fontSize: 16, fontWeight: '600' },
});
