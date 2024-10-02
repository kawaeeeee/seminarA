# seminarA
ゼミAのコード

## Kubernetesをもちいて分散処理を実装しました
下記の画像を生成する、ray-tracingの処理を分散処理しました。
![image10000](https://github.com/user-attachments/assets/50cf6e10-968a-4c04-900d-af6521db48e2)

## 実装方法
次のように、producerのpodがconsumerのpodに計算範囲を、指示する。
consumerは計算が終わると、producerに計算結果を返す。
producer-consumer間の通信はTCPで行う。
<img width="1441" alt="スクリーンショット 2024-10-02 122130" src="https://github.com/user-attachments/assets/0c30b5f3-2ad7-4585-9484-09b4ca0240b5">

## 実行結果
<img width="1319" alt="スクリーンショット 2024-10-02 122212" src="https://github.com/user-attachments/assets/0b2cb173-36f1-4dcf-a696-634def13c2c1">
