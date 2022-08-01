Use the https://github.com/ulfalizer/Kconfiglib
need install `kconfiglib==14.1.0`
for windows need install `windows-curses`

</br>

1. config cmd: 
    - create `build/IoTOSconfig` file
    - run menuconfig 
        - create `build/tuya_iot.config`
        - create`apps/xxx/app_config.h`
        - copy `build/tuya_iot.config` to `apps/xxx/tuya_iot.config`

2. build apps cmd:
    - if have `apps/xxx/tuya_iot.config`
        - copy `apps/xxx/tuya_iot.config` to `build/tuya_iot.config`
        - create `apps/xxx/app_config.h`
    - if not have `apps/xxx/tuya_iot.config`
        - run menuconfig 
            - create default `build/tuya_iot.config`
            - create`apps/xxx/app_config.h`
            - copy `build/tuya_iot.config` to `apps/xxx/tuya_iot.config`

3. build samples cmd:
    - check if build samples or apps in `ide_tool_front` of `ide_tool.py`
    - if build samples, don't auto kconfig
    - if build apps, auto kconfig
