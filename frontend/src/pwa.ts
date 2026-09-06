import { registerSW } from "virtual:pwa-register";

registerSW({
  immediate: true,

  onRegisteredSW(swUrl, registration) {
    console.log("Service worker registered:", swUrl);

    if (registration) {
      console.log("PWA registration active");
    }
  },

  onRegisterError(error) {
    console.error("Service worker registration failed:", error);
  },
});