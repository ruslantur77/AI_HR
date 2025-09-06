import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

export async function startEchoSession() {
  const pc = new RTCPeerConnection({iceServers: [{urls: 'stun:stun.l.google.com:19302'}]});
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {sampleRate: 16000, channelCount: 1, echoCancellation: false}
  });
  stream.getTracks().forEach(tr => pc.addTrack(tr, stream));

  await new Promise(res => {
    if (pc.iceGatheringState === 'complete') res();
    else pc.addEventListener('icegatheringstatechange', () => pc.iceGatheringState === 'complete' && res());
  });

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  const {data: answer} = await axios.post(`${API_URL}/api/stt/offer`, {sdp: offer.sdp, type: offer.type});
  await pc.setRemoteDescription(answer);
  return {pc, stream};
}