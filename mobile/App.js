/**
 * App.js — the entry point of the Expo mobile app.
 *
 * WHAT THIS FILE DOES:
 *   Sets up React Navigation with three screens:
 *   1. Camera (home screen) — take photos for PPE detection
 *   2. Results — show YOLO detection results
 *   3. History — show past detection logs from the database
 *
 * HOW NAVIGATION WORKS:
 *   React Navigation manages a "stack" of screens.
 *   Think of it like a stack of cards:
 *     - The app starts on Camera (bottom of the stack)
 *     - When you navigate to Results, it goes on top
 *     - Pressing "back" removes the top card, revealing Camera again
 *
 * CONNECTIONS:
 *   - CameraScreen.js → navigates to ResultScreen with detection data
 *   - ResultScreen.js → navigates back to CameraScreen for a new scan
 *   - CameraScreen.js → navigates to HistoryScreen to view past logs
 */

import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";

import CameraScreen from "./src/screens/CameraScreen";
import ResultScreen from "./src/screens/ResultScreen";
import HistoryScreen from "./src/screens/HistoryScreen";

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <>
      <StatusBar style="light" />
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Camera"
          screenOptions={{
            headerStyle: { backgroundColor: "#1a1a2e" },
            headerTintColor: "#FFD700",
            headerTitleStyle: { fontWeight: "bold" },
            contentStyle: { backgroundColor: "#1a1a2e" },
          }}
        >
          <Stack.Screen
            name="Camera"
            component={CameraScreen}
            options={{ headerShown: false }}
          />
          <Stack.Screen
            name="Results"
            component={ResultScreen}
            options={{ title: "Detection Results" }}
          />
          <Stack.Screen
            name="History"
            component={HistoryScreen}
            options={{ title: "Detection History" }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </>
  );
}
