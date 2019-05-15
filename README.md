# SpineConverter2.1.27
Conversion tool between .skel and .json files, Spine version 2.1.27.
Originally made to make free animation modding of the game Darkest Dungeon possible.
Due to personal problems I don't have the time to continue working on it.
Tested against Darkest Dungeon's .skel files.
## Requirements:
Python 3
## Usage
Reading and writing .skel files:
```
from spBinaryReader import spBinaryReader
from spBinaryWriter import spBinaryWriter
reader = spBinaryReader()
writer = spBinaryWriter()
skeletonData = reader.readSkeletonDataFile( "vestal.sprite.walk.skel" )
writer.writeSkeletonDataFile( skeletonData, "vestal.sprite.walk.reexported.skel" )
```
Reading and writing .json files:
```
from spJsonWriter import spJsonWriter
from spJsonReader import spJsonReader
reader = spJsonReader()
writer = spJsonWriter()
skeletonData = reader.readSkeletonDataFile( "vestal.sprite.walk.json" )
writer.writeSkeletonDataFile( skeletonData, "vestal.sprite.walk.reexported.json" )
```
Reading .skel file and writing .json file (can do the opposite):
```
from spBinaryReader import spBinaryReader
from spJsonWriter import spJsonWriter
binaryReader = spBinaryReader()
jsonWriter = spJsonWriter()
skeletonData = binaryReader.readSkeletonDataFile( "vestal.sprite.walk.skel" )
jsonWriter.writeSkeletonDataFile( skeletonData, "vestal.sprite.walk.json" )
```
Reading and writing .atlas files:
```
from spAtlas import *
atlas = readAtlasFile( "vestal.sprite.walk.atlas" )
writeAtlasFile( atlas, "vestal.sprite.walk.reexported.atlas" )
```
## Notes
- Skeleton data that's returned by *Reader classes is not made to be passed to runtimes, it's just stored data.
- Skeleton data is perfectly "jsonable", it's all dictionaries and lists, no classes.
- Produced .json doesn't have all floats rounded, like official ones do, only floats like 1.0 are turned into integers. That's done to preserve precision. So reading binary -> writing json -> reading json -> writing binary produces exact same binary. Value -0.0 is left for the same reason. SkeletonViewer doesn't have any problem loading such files.
- **cc_shrew.skel** has instances of two slot color timelines one after the other. That creates problems with json since timeline types are used as keys, so the second one will override the first one. It's unclear if that was an exporter bug or Spine's json exports allow duplicate keys. An ugly hack is used to bypass that problem.
- 2.1.27 SkeletonViewer expects json to have slot blend property as "additive". Some 2.1.27 jsons have it as "blend".
spJsonReader will try to read both. spJsonWriter will write with slot["additive"] = True. If you want to write slot["blend"] = "additive" instead - set blendProperty to True:
`
jsonWriter.writeSkeletonDataFile( skeletonData, "vestal.sprite.walk.json", blendProperty=True )
`
## Thanks
- semgilo for his binary reading code for 2.1.27: https://github.com/semgilo/spine-runtime-binary-c
- archive.org for archived 2.1.27 compatible version of SkeletonViewer: https://web.archive.org/web/20150216033632/http://esotericsoftware.com/spine-skeleton-viewer
- Recaf project: https://github.com/Col-E/Recaf
