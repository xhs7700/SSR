package com.example.ssrmobile;

public class Device {
    public final int id;
    public final String status,name;

    Device(int id,String status,String name){
        this.id=id;
        this.status=status;
        this.name=name;
    }

    @Override
    public String toString() {
        return "Device{" +
                "id=" + id +
                ", status='" + status + '\'' +
                ", name='" + name + '\'' +
                '}';
    }
}
