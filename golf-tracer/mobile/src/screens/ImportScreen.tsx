import * as ImagePicker from 'expo-image-picker';
import React, { useEffect } from 'react';
import { ActivityIndicator, Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import { useVideoUpload } from '../hooks/useVideoUpload';
import type { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Import'>;

export default function ImportScreen({ navigation }: Props) {
  const { state, upload, reset } = useVideoUpload();

  useEffect(() => {
    pickVideo();
  }, []);

  async function pickVideo() {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission required', 'Gallery access is needed to import videos.', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Videos,
      quality: 1,
      allowsEditing: false,
    });

    if (result.canceled) {
      navigation.goBack();
      return;
    }

    const asset = result.assets[0];
    const filename = asset.fileName ?? `import_${Date.now()}.mp4`;
    try {
      const { video, job } = await upload(asset.uri, filename);
      navigation.replace('Processing', { videoId: video.id, jobId: job.id });
    } catch (err: any) {
      Alert.alert('Upload failed', err.message, [
        { text: 'Try Again', onPress: () => { reset(); pickVideo(); } },
        { text: 'Cancel', onPress: () => navigation.goBack() },
      ]);
    }
  }

  return (
    <View style={styles.container}>
      {state.phase === 'uploading' ? (
        <>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={styles.text}>Uploading {Math.round(state.progress * 100)}%</Text>
        </>
      ) : (
        <>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={styles.text}>Opening gallery…</Text>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background, justifyContent: 'center', alignItems: 'center', gap: 20 },
  text: { color: Colors.textSecondary, fontSize: 16 },
});
