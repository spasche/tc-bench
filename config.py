import os

LAYERS = [
'Orte',
'PointsHotel',
'PointsBedBreak',
'PointsJugen',
'PointsBackpacker',
'PointsGruppen',
'PointsUbernachten',
'PointsBauernhof',
'PointsFerien',
'PointsCamping',
'Slowup',
'Kantone',
'Gemeinden',
'VelolandRoutenRegional',
'VelolandRoutenNational',
'VelolandEtappenRegional',
'VelolandEtappenNational',
'VelolandService',
'VelolandMiet',
'VelolandBahnBusSchiff',
'VelolandLokaleAngebote',
'Wanderwegnetz',
'WanderlandRoutenRegional',
'WanderlandEtappenRegional',
'WanderlandEtappenNational',
'WanderlandRoutenNational',
'WanderlandBahnBusSchiff',
'WanderlandLokaleAngebote',
'MtblandRoutenNational',
'MtblandRoutenRegional',
'MtblandEtappenNational',
'MtblandEtappenRegional',
'MtblandLokaleAngebote',
'MtblandBahnBusSchiff',
'MtblandMiet',
'MtblandService',
'SkatinglandRoutenNational',
'SkatinglandRoutenRegional',
'SkatinglandEtappenNational',
'SkatinglandEtappenRegional',
'SkatinglandLokaleAngebote',
'SkatinglandBahnBusSchiff',
'KanulandRoutenRegional',
'KanulandEtappenRegional',
'KanulandEtappenNational',
'KanulandRoutenNational',
'KanulandRafting',
'KanulandBahnBusSchiff',
'KanulandClub',
'KanulandBbangebote',
'OffentlicherBahn',
'OffentlicherBus',
'OffentlicherTramBus',
'OffentlicherSchiff',
'OffentlicherSeilbahn',
'OffentlicherStandseilbahn',
'NaturLandschaft',
'IVS',
'Migros'
]

BBOXES = [
  # '535200,170800,548000,183600'
  '573600,183600,599200,209200',
  '701600,132400,727200,158000',
  '701600,132400,727200,158000',
  # zoomed more
  '696480,265520,701600,270640',
  '594080,168240,599200,173360',
  '716960,168240,722080,173360',
  '722080,265520,727200,270640',
]

BBOX = BBOXES[0]

TILES_URL = "http://%(server)s/tilecache?FORMAT=image/png&LAYERS=%(layers)s&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&SRS=EPSG:21781&BBOX=%(bbox)s&WIDTH=256&HEIGHT=256"

DATA_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), 'data'))
TC_CONFIG_IN = os.path.join(DATA_PATH, "tilecache.cfg.in")
