// src/components/hooks/useInterview.js
import axios from '../../api/axios';   // ваш инстанс с токеном / baseURL

export async function startEchoSession(interviewId) {
  const pc = new RTCPeerConnection({
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
  });

  const stream = await navigator.mediaDevices.getUserMedia({
    audio: { sampleRate: 16000, channelCount: 1, echoCancellation: false }
  });
  stream.getTracks().forEach(tr => pc.addTrack(tr, stream));

  await new Promise(res => {
    if (pc.iceGatheringState === 'complete') res();
    else pc.addEventListener('icegatheringstatechange', () => pc.iceGatheringState === 'complete' && res());
  });

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  // новый энд-поинт из OpenAPI
  const { data } = await axios.post(
    `/api/interview/rtc/offer/${interviewId}`,
    { sdp: offer.sdp, type: offer.type }
  );

  await pc.setRemoteDescription(data);
  return { pc, stream };
}