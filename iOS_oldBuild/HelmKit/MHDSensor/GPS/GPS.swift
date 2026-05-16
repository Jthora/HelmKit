//
//  GPS.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/19/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import CoreLocation

class GPS:NSObject, CLLocationManagerDelegate {
    
    // Singleton
    private static var _shared:GPS?
    static var shared:GPS {
        _shared = _shared ?? GPS()
        return _shared!
    }
    
    let locationManager = CLLocationManager()
    
    var isTracking:Bool = false
    
    private var updateHeadingCallbacks:[String:((CLHeading) -> Void)] = [:]
    func set(updateHeadingCallback: @escaping ((CLHeading) -> Void), functionName:StaticString = #function, lineNumber: Int = #line) {
        let key = "\(functionName)\(lineNumber)"
        updateHeadingCallbacks[key] = updateHeadingCallback
    }
    
    
    override init() {
        super.init()
    }
    
    func startTracking() {
        isTracking = true
        
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.distanceFilter = 0.0001
        locationManager.headingFilter = kCLHeadingFilterNone
        
        if CLLocationManager.headingAvailable() { locationManager.startUpdatingHeading() }
    }
    func stopTracking() {
        isTracking = false
        
        locationManager.stopUpdatingLocation()
    }
    
    
    func locationManager(_ manager: CLLocationManager, didUpdateHeading newHeading: CLHeading) {
        for (_,callback) in updateHeadingCallbacks {
            callback(newHeading)
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        stopTracking()
    }
}
