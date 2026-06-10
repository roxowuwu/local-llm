#!/bin/bash

# If no argument given
if [ -z "$1" ]; then
  echo "Usage: ./bot.sh [study|game|entertainment|mute|unmute|info|greet]"
  exit
fi

case $1 in

  
  study)
    echo "Entering Study Mode..."
    google-chrome &
    code &
    ;;

  
  game)
    echo "Entering Game Mode..."
    steam &
    ;;

  
  entertainment)
    echo "Entering Entertainment Mode..."
    spotify &
    ;;

  
  mute)
    echo "Muting system..."

    if command -v amixer >/dev/null 2>&1; then
      amixer set Master mute
    elif command -v pactl >/dev/null 2>&1; then
      pactl set-sink-mute @DEFAULT_SINK@ 1
    else
      echo "Audio control not supported"
    fi
    ;;

  
  unmute)
    echo "Unmuting system..."

    if command -v amixer >/dev/null 2>&1; then
      amixer set Master unmute
    elif command -v pactl >/dev/null 2>&1; then
      pactl set-sink-mute @DEFAULT_SINK@ 0
    else
      echo "Audio control not supported"
    fi
    ;;

  
  info)
    echo "System Information:"
    uname -a
    ;;

  
  greet)
    echo "Hello $2"
    ;;

open)
  echo "Searching for $2..."

  if [ -z "$2" ]; then
    echo "Please specify an application"
    exit
  fi

  # 1. Manual mapping (important for web apps)
  case $2 in
    youtube)
      google-chrome --app=https://youtube.com &
      exit
      ;;
    cs2|counterstrike)
      steam steam://rungameid/730 &
      exit
      ;;
  esac

  # 2. Try exact command
  if command -v "$2" >/dev/null 2>&1; then
    echo "Opening $2..."
    $2 &
    exit
  fi

  # 3. Search in .desktop files
  app_file=$(grep -ril "$2" /usr/share/applications ~/.local/share/applications 2>/dev/null | head -n 1)

  if [ -n "$app_file" ]; then
    echo "Found GUI app: $app_file"

    # Extract Exec line
    exec_cmd=$(grep -i "^Exec=" "$app_file" | head -n 1 | cut -d= -f2)

    # Remove %U, %u, etc.
    exec_cmd=$(echo "$exec_cmd" | sed 's/ *%[a-zA-Z]//g')

    echo "Running: $exec_cmd"
    eval "$exec_cmd &"
  else
    echo "No matching application found"
  fi
  ;;
  
  *)
    echo "Usage: ./bot.sh [study|game|entertainment|mute|unmute|info|greet]"
    ;;
echo "Enter command:"
read command

echo "$command" | python3 brain.py
esac
