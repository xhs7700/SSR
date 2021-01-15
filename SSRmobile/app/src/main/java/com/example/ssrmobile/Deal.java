package com.example.ssrmobile;

public class Deal {
    public final String place;
    public final String device;
    public final int deviceId;
    public final long timeStart,timeEnd;

    public Deal(String place, String device, int deviceId, long timeStart, long timeEnd) {
        this.place = place;
        this.device = device;
        this.deviceId = deviceId;
        this.timeStart = timeStart;
        this.timeEnd = timeEnd;
    }

    @Override
    public String toString() {
        return "Deal{" +
                "place='" + place + '\'' +
                ", device='" + device + '\'' +
                ", deviceId=" + deviceId +
                ", timeStart=" + timeStart +
                ", timeEnd=" + timeEnd +
                '}';
    }
}
