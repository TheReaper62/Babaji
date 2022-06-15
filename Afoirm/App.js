import axios from 'axios';
import registerNNPushToken from 'native-notify';
import { StatusBar } from 'expo-status-bar';
import React, {useState} from 'react';
import { StyleSheet, Text, View, Button } from 'react-native';



function buttonpress() {
  console.log("Ahhhhh it hurts")
  console.log(`Before you pressed me, count was ${count}`)
  setCount(count+1)
}

export default function App() {
  registerNNPushToken(2960, 'AkBsj1bVoC7DXXJuKkmF4Z');

  let [count, setCount] = useState(0)

  function buttonpress() {
    console.log("Ahhhhh it hurts")
    console.log(`Before you pressed me, count was ${count}`)
    setCount(count+1)
  }

  return (
    <View style={styles.container}>
      <Text>Click the button below!</Text>
        <Button title="Press me!!" onPress={buttonpress}></Button>
      <Text>You have press it {count} times </Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  Button: {
    width: 100,
    height: 50,
  }
});
