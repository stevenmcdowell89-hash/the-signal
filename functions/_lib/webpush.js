// Minimal Web Push (RFC 8030 + RFC 8291 aes128gcm + RFC 8292 VAPID)
// for Cloudflare Pages Functions. Uses Web Crypto primitives only.

const enc = new TextEncoder();

function b64urlEncode(buf) {
  const bytes = new Uint8Array(buf);
  let s = "";
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function b64urlDecode(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  const bin = atob(s);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function concat(...arrays) {
  let total = 0;
  for (const a of arrays) total += a.length;
  const out = new Uint8Array(total);
  let offset = 0;
  for (const a of arrays) { out.set(a, offset); offset += a.length; }
  return out;
}

async function importVapidPrivate(jwkJson) {
  const jwk = JSON.parse(jwkJson);
  return crypto.subtle.importKey(
    "jwk",
    { kty: jwk.kty, crv: jwk.crv, x: jwk.x, y: jwk.y, d: jwk.d, ext: true, key_ops: ["sign"] },
    { name: "ECDSA", namedCurve: "P-256" },
    false,
    ["sign"],
  );
}

async function signVapidJwt(privateKey, audience, subject) {
  const header = { typ: "JWT", alg: "ES256" };
  const payload = { aud: audience, exp: Math.floor(Date.now() / 1000) + 12 * 3600, sub: subject };
  const h = b64urlEncode(enc.encode(JSON.stringify(header)));
  const p = b64urlEncode(enc.encode(JSON.stringify(payload)));
  const signingInput = `${h}.${p}`;
  const sig = await crypto.subtle.sign(
    { name: "ECDSA", hash: { name: "SHA-256" } },
    privateKey,
    enc.encode(signingInput),
  );
  return `${signingInput}.${b64urlEncode(sig)}`;
}

// Encrypts `plaintext` for a given subscription, returning the aes128gcm body.
async function encryptPayload(plaintext, p256dh, auth) {
  const ephemeral = await crypto.subtle.generateKey(
    { name: "ECDH", namedCurve: "P-256" },
    true,
    ["deriveBits"],
  );

  const userPub = await crypto.subtle.importKey(
    "raw", p256dh, { name: "ECDH", namedCurve: "P-256" }, true, [],
  );

  // ECDH shared secret
  const shared = await crypto.subtle.deriveBits(
    { name: "ECDH", public: userPub }, ephemeral.privateKey, 256,
  );

  // Ephemeral public (uncompressed 65 bytes)
  const asPub = new Uint8Array(await crypto.subtle.exportKey("raw", ephemeral.publicKey));

  // Step 1: HKDF(shared, salt=auth, info="WebPush: info\0" + ua_pub + as_pub) → IKM'
  const sharedKey = await crypto.subtle.importKey("raw", shared, { name: "HKDF" }, false, ["deriveBits"]);
  const info1 = concat(enc.encode("WebPush: info"), new Uint8Array([0]), p256dh, asPub);
  const ikmPrime = new Uint8Array(await crypto.subtle.deriveBits(
    { name: "HKDF", hash: "SHA-256", salt: auth, info: info1 },
    sharedKey, 256,
  ));

  // Step 2: random salt; derive CEK + NONCE from IKM'
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const ikmKey = await crypto.subtle.importKey("raw", ikmPrime, { name: "HKDF" }, false, ["deriveBits"]);
  const cek = await crypto.subtle.deriveBits(
    { name: "HKDF", hash: "SHA-256", salt, info: concat(enc.encode("Content-Encoding: aes128gcm"), new Uint8Array([0])) },
    ikmKey, 128,
  );
  const nonce = await crypto.subtle.deriveBits(
    { name: "HKDF", hash: "SHA-256", salt, info: concat(enc.encode("Content-Encoding: nonce"), new Uint8Array([0])) },
    ikmKey, 96,
  );

  // Step 3: pad plaintext (single-record, last) and AES-GCM encrypt
  const padded = concat(plaintext, new Uint8Array([0x02]));
  const cekKey = await crypto.subtle.importKey("raw", cek, { name: "AES-GCM" }, false, ["encrypt"]);
  const ciphertext = new Uint8Array(await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: new Uint8Array(nonce), tagLength: 128 },
    cekKey, padded,
  ));

  // Frame: salt(16) || rs(4 BE) || keyid_len(1) || keyid(65) || ciphertext
  const rs = 4096;
  const rsBytes = new Uint8Array([(rs >>> 24) & 0xff, (rs >>> 16) & 0xff, (rs >>> 8) & 0xff, rs & 0xff]);
  return concat(salt, rsBytes, new Uint8Array([asPub.length]), asPub, ciphertext);
}

// Send a push to a single subscription. Returns the upstream Response.
export async function sendPush(subscription, payloadJson, vapidPrivateJwk, vapidPublicB64, subject) {
  const p256dh = b64urlDecode(subscription.keys.p256dh);
  const auth = b64urlDecode(subscription.keys.auth);

  const body = await encryptPayload(enc.encode(payloadJson), p256dh, auth);

  const endpointUrl = new URL(subscription.endpoint);
  const audience = `${endpointUrl.protocol}//${endpointUrl.host}`;
  const privateKey = await importVapidPrivate(vapidPrivateJwk);
  const jwt = await signVapidJwt(privateKey, audience, subject || "mailto:noreply@example.com");

  return fetch(subscription.endpoint, {
    method: "POST",
    headers: {
      "Authorization": `vapid t=${jwt}, k=${vapidPublicB64}`,
      "Content-Encoding": "aes128gcm",
      "Content-Type": "application/octet-stream",
      "TTL": "86400",
    },
    body,
  });
}
