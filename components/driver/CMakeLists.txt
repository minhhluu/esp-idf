idf_build_get_property(target IDF_TARGET)

if(${target} STREQUAL "linux")
    return() # This component is not supported by the POSIX/Linux simulator
endif()

# Always compiled source files
set(srcs)

# Always included headers
set(includes "deprecated"
             "i2c/include"
             "touch_sensor/include"
             "twai/include")

# Always included linker fragments
set(ldfragments "")

# ADC related source files (deprecated)
if(CONFIG_SOC_ADC_SUPPORTED)
    list(APPEND srcs "deprecated/adc_legacy.c")

    if(CONFIG_SOC_ADC_DMA_SUPPORTED)
        list(APPEND srcs "deprecated/adc_dma_legacy.c")
    endif()
endif()

# I2C related source files
if(CONFIG_SOC_I2C_SUPPORTED)
    list(APPEND srcs "i2c/i2c.c")
endif()

# MCPWM legacy driver
if(CONFIG_SOC_MCPWM_SUPPORTED)
    list(APPEND srcs "deprecated/mcpwm_legacy.c")
endif()

# RMT legacy driver
if(CONFIG_SOC_RMT_SUPPORTED)
    list(APPEND srcs "deprecated/rmt_legacy.c")
endif()

# Sigma-Delta Modulation legacy driver
if(CONFIG_SOC_SDM_SUPPORTED)
    list(APPEND srcs "deprecated/sigma_delta_legacy.c")
endif()

# Touch Sensor related source files
if(CONFIG_SOC_TOUCH_SENSOR_SUPPORTED)
    if(CONFIG_SOC_TOUCH_SENSOR_VERSION LESS 3)
        list(APPEND srcs "touch_sensor/touch_sensor_common.c"
                        "touch_sensor/${target}/touch_sensor.c")
        list(APPEND includes "touch_sensor/${target}/include")
    endif()
endif()

# TWAI related source files
# TWAIFD is not supported by the legacy driver
if(CONFIG_SOC_TWAI_SUPPORTED AND NOT CONFIG_SOC_TWAI_SUPPORT_FD)
    list(APPEND srcs "twai/twai.c")
    list(APPEND ldfragments "twai/linker.lf")
endif()

# Other source files
if(${target} STREQUAL "esp32")
    list(APPEND srcs "deprecated/adc_i2s_deprecated.c")
endif()

if(BOOTLOADER_BUILD)
    # Bootloader shall NOT depend on the drivers
    idf_component_register()
else()
    # (REQUIRES cannot hide soc headers, since many arguments in the driver headers are chip-dependent)
    # (Legacy drivers requires `esp_adc`, due to ADC HW resource mutex logics are there.
    # Can be removed together with legacy drivers)
    idf_component_register(SRCS "${srcs}"
                           INCLUDE_DIRS ${includes}
                           PRIV_REQUIRES efuse esp_timer esp_mm
                           REQUIRES esp_pm esp_ringbuf freertos soc hal esp_hw_support
                           # for backward compatibility, the driver component needs to
                           # have a public dependency on other "esp_driver_foo" components
                                    esp_driver_gpio esp_driver_pcnt esp_driver_gptimer esp_driver_spi esp_driver_mcpwm
                                    esp_driver_ana_cmpr esp_driver_i2s esp_driver_sdmmc esp_driver_sdspi esp_driver_sdio
                                    esp_driver_dac esp_driver_rmt esp_driver_tsens esp_driver_sdm esp_driver_i2c
                                    esp_driver_uart esp_driver_ledc esp_driver_parlio esp_driver_usb_serial_jtag
                                    esp_driver_twai
                           LDFRAGMENTS ${ldfragments}
                          )
    if(CONFIG_SOC_ADC_SUPPORTED AND
       CONFIG_COMPILER_STATIC_ANALYZER AND CMAKE_C_COMPILER_ID STREQUAL "GNU") # TODO GCC-366
        set_source_files_properties(deprecated/adc_legacy.c
                                    PROPERTIES COMPILE_FLAGS "-Wno-analyzer-use-of-uninitialized-value")
    endif()
endif()
