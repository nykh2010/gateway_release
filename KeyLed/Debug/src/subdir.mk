################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../src/key.c \
../src/led.c \
../src/main.c \
../src/mylist.c \
../src/statusmonitor.c \
../src/sysmonitor.c 

OBJS += \
./src/key.o \
./src/led.o \
./src/main.o \
./src/mylist.o \
./src/statusmonitor.o \
./src/sysmonitor.o 

C_DEPS += \
./src/key.d \
./src/led.d \
./src/main.d \
./src/mylist.d \
./src/statusmonitor.d \
./src/sysmonitor.d 


# Each subdirectory must supply rules for building sources it contributes
src/%.o: ../src/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: GCC C Compiler'
	arm-poky-linux-gnueabi-gcc -I"/home/xulingfeng/eclipse-workspace/KeyLed/src" -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


