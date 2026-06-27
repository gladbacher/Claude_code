import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Colors } from '../constants/colors';
import type { RootStackParamList } from './types';

import HomeScreen from '../screens/HomeScreen';
import RecordScreen from '../screens/RecordScreen';
import ImportScreen from '../screens/ImportScreen';
import ProcessingScreen from '../screens/ProcessingScreen';
import ResultScreen from '../screens/ResultScreen';
import CorrectionScreen from '../screens/CorrectionScreen';
import ExportScreen from '../screens/ExportScreen';

const Stack = createStackNavigator<RootStackParamList>();

export default function RootNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: { backgroundColor: Colors.background },
          headerTintColor: Colors.textPrimary,
          headerTitleStyle: { fontWeight: 'bold' },
          contentStyle: { backgroundColor: Colors.background },
        }}
      >
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Golf Tracer' }} />
        <Stack.Screen name="Record" component={RecordScreen} options={{ title: 'Record Swing', headerShown: false }} />
        <Stack.Screen name="Import" component={ImportScreen} options={{ title: 'Import Video' }} />
        <Stack.Screen name="Processing" component={ProcessingScreen} options={{ title: 'Analysing Swing', headerLeft: () => null }} />
        <Stack.Screen name="Result" component={ResultScreen} options={{ title: 'Tracer Result' }} />
        <Stack.Screen name="Correction" component={CorrectionScreen} options={{ title: 'Manual Corrections' }} />
        <Stack.Screen name="Export" component={ExportScreen} options={{ title: 'Export Video' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
