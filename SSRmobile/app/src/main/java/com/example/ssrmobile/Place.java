package com.example.ssrmobile;

import java.util.ArrayList;

public class Place {
    public final double longitude, latitude;
    public final String name;
    public final int id;
    public ArrayList<Device> devices;


    public Place(double longitude, double latitude, String name, int id, ArrayList<Device> devices) {
        this.longitude = longitude;
        this.latitude = latitude;
        this.name = name;
        this.id = id;
        this.devices = devices;
    }

    @Override
    public String toString() {
        return "Place{" +
                "name='" + name + '\'' +
                ", id=" + id +
                ", devices=" + devices +
                '}';
    }
}
