// O MapLibre 6 (build ESM) procura o worker em `./maplibre-gl-worker.mjs`, ao lado do próprio arquivo.
// Depois do build do Vite esse arquivo não existe em assets/, e o mapa falha com "Worker failed to load".
// Aqui o Vite empacota o worker (com as dependências) e o MapLibre passa a usar a URL certa.
// Importar este módulo antes de criar qualquer mapa.
import { setWorkerUrl } from 'maplibre-gl';
import urlDoWorker from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';

setWorkerUrl(urlDoWorker);
