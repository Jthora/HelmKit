//
//  MagnetoMeter.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/19/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import CoreMotion


// Magnetic/Cyclic/Spatial Flux
class FluxSensor:NSObject {
    
    private let sampleQueue = OperationQueue()
    
    // Singleton
    private static var _shared:FluxSensor?
    static var shared:FluxSensor {
        _shared = _shared ?? FluxSensor()
        return _shared!
    }
    
    let motionManager = CMMotionManager()
    var isTracking:Bool = false
    
    private var updateMagnetometerCallbacks:[String:((CMMagnetometerData?) -> Void)] = [:]
    func set(updateMagnetometerCallback: @escaping ((CMMagnetometerData?) -> Void), key:String = "default") {
        updateMagnetometerCallbacks[key] = updateMagnetometerCallback
    }
    
    private var updateGyroCallbacks:[String:((CMGyroData?) -> Void)] = [:]
    func set(updateGyroCallback: @escaping ((CMGyroData?) -> Void), key:String = "default") {
        updateGyroCallbacks[key] = updateGyroCallback
    }
    
    private var updateMotionCallbacks:[String:((CMDeviceMotion?) -> Void)] = [:]
    func set(updateMotionCallback: @escaping ((CMDeviceMotion?) -> Void), key:String = "default") {
        updateMotionCallbacks[key] = updateMotionCallback
    }
    
    override init() {
        super.init()
    }
    
    func startTracking(magnetometerOnly:Bool = false) {
        isTracking = true
        motionManager.startMagnetometerUpdates()
        
        if !magnetometerOnly {
            if motionManager.isDeviceMotionAvailable {
                motionManager.startDeviceMotionUpdates(to: sampleQueue, withHandler: { (deviceMotion, error) in
                    for (_,callback) in self.updateMotionCallbacks {
                        callback(deviceMotion)
                    }
                })
            }
            if motionManager.isGyroAvailable {
                motionManager.startGyroUpdates(to: sampleQueue) { (data, error) in
                    for (_,callback) in self.updateGyroCallbacks {
                        callback(data)
                    }
                }
            }
        }
        
        if motionManager.isMagnetometerAvailable {
            motionManager.startMagnetometerUpdates(to: sampleQueue) { (data, error) in
                for (_,callback) in self.updateMagnetometerCallbacks {
                    callback(data)
                }
            }
        }
    }
    
    func stopTracking() {
        isTracking = false
        
        if motionManager.isDeviceMotionAvailable {
            motionManager.stopDeviceMotionUpdates()
        }
        if motionManager.isGyroAvailable {
            motionManager.stopGyroUpdates()
        }
        if motionManager.isMagnetometerAvailable {
            motionManager.stopMagnetometerUpdates()
        }
    }
}
