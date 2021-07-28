// Program to illustrate the working of
// objects and class in C++ Programming

#include <iostream>
using namespace std;

/**
 * @brief My best Room class
 * @details More Room details
 * 
 */
class Room {

   public:
    int length;
    double breadth;
    long height;

    /**
     * @brief calculateArea class 
     * 
     * @return double 
     */
    double calculateArea() {
        return length * breadth;
    }

    /**
     * @brief calculateVolume class 
     * 
     * @return double 
     */
    double calculateVolume() {
        return length * breadth * height;
    }
};

/**
 * @brief My better Car classes
 * @details More Car details
 * 
 */
class Car {
    public:
        int wheelCount;
        bool fast;

    bool isFast() {
        return fast;
    }

    /**
     * @brief Set the Wheel Count object
     * @ 
     * 
     * @param wheelCount as my int
     */
    void setWheelCount(int wheelCount) {
        wheelCount = wheelCount;
    }

    /**
     * @brief Get the Wheel Count object
     * 
     * @return int wheelCount as number
     */
    int getWheelCount() {
        return wheelCount;
    }
};

int main() {

    // create object of Room class
    Room room1;

    // assign values to data members
    room1.length = 42.5;
    room1.breadth = 30.8;
    room1.height = 19.2;

    // calculate and display the area and volume of the room
    cout << "Area of Room =  " << room1.calculateArea() << endl;
    cout << "Volume of Room =  " << room1.calculateVolume() << endl;

    return 0;
}