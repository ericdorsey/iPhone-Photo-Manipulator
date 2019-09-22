### iPhone Photo Manipulator

#### What Is This
A helper script to wrangle photos dumped off an iPhone to OSX, then modified, then added back to the iPhone via AirDrop (or whatever other means).

#### TL;DR

Allows multiple helper operations against a folder of photos dumped from an iPhone onto OSX via Image Capture:
* Remove `.AAE` files
* Rename `.JPG` files (desireable because of naming conflits)
* Strip EXIF date data (to control sorting when added back to iPhone (via Airdop, etc)

#### !TL;DR

When the Photos app on my iPhone gets entirely too fulll I will dump photos to OSX via the built in OSX Image Capture application. Usually I'll dump them to a folder called `YYYY-MM-DD_iPhonePhotosDump`.

There are often select photos I want to add back to the device. If you add them back without modification you're at the mercy of the EXIF date data for how they're organized in the Photos app. 

If consolidating multiple `YYYY-MM-DD_iPhonePhotosDump` folders into folders (say `Pets`, `Family`, etc) on OSX, there are several potential issues:

* Dumped photos have `.AAE` sidecar / meta files (ref: https://apple.stackexchange.com/questions/334901/what-is-the-purpose-of-an-aae-file) which I generally want to get rid of. This can be done with `find . -name "*.AAE" -type f`  and then `find . -name "*.AAE" -type f -delete`, but when combined with other manipulation I want to do on the photos this can get tiresome. 
* There will be name conflicts if you have enough photos. When dumping photos onto OSX they will often have a name like `IMG_XXXX.JPG`, where `XXXX` is some series of numbers like 4359, 4360, 4361, etc. If you have a lot of `Pets` photos in various `YYYY-MM-DD_iPhonePhotosDump` folders you'll eventually get two distinct photos with a name like `IMG_4535.JPG`. Manually renaming those would suck. 
* When adding photos back to your phone from multiple `YYYY-MM-DD_iPhonePhotosDump` folders sorting is based on the EXIF data on the photo. This may or may not be desireable.
* Dumping Image Capture sometimes results in weird image name issues. Batches of photos from different times may a name conflict; a series of photos from one day might have `IMG_5568.JPG` as their names, and another set from a different time might have `IMG_5568 1.JPG` in their name. When sorting on OSX for organization, this ends up in an annoying every other photo being from the first set and then the second set. Renaming all the `XXXX 1.JPG` or `XXXX 2.JPG` thus becomes desireable at times.

#### Help
Use `$ ./iphone-photo-manip.py -h`, ex:

```
~/scripts/img_renamer $ ./iphone-photo-manip.py -h
usage: iphone-photo-manip.py [-h] [-d DIR] [-r] [-f FILE] [-w] [-c] [-s]
                             [-n NUMBERSPACED]

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     run this script against files in supplied directory
  -r, --removeaae       delete the .aae files; for use with --directory
                        argument
  -f FILE, --file FILE  run this script against only supplied file name
  -w, --whatif          what if; dry run
  -c, --changenames     change filename(s), rename (all) file(s)
  -s, --stripexifdates  strip exif dates from file(s)
  -n NUMBERSPACED, --numberspaced NUMBERSPACED
                        integer; for XXXX 1.JPG style filename renames. For
                        use with -c
```

#### Helpful Links

* https://realpython.com/python-logging/ 
* https://stackoverflow.com/questions/13857788/python-logging-debug-level-doesnt-logging/13858009#13858009
