//
//  MultiMagnetometer.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/19/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import CoreMotion
import CoreLocation

protocol MultiMagnetometerDelegate {
    
    // Magnetic
    func updateCalibratedMagneticHeading(x:Double, y:Double, z:Double, m:Double, s:Double)
    func updateMagneticHeading(x:Double)
    func updateHeading(x:Double, y:Double, z:Double, m:Double, s:Double)
    func updateMagnetometer(x:Double, y:Double, z:Double, m:Double, s:Double)
    
    // Spacial
    func updateAcceleration(x:Double, y:Double, z:Double, m:Double)
    func updateAttitude(roll:Double, yaw:Double, pitch:Double, matrix:CMRotationMatrix)
    func updateGravity(x:Double, y:Double, z:Double, m:Double)
    func updateGyro(x:Double, y:Double, z:Double, m:Double)
}

class MultiMagnetometer: NSObject {
    
    private let DELTA:Double = 128 // Scale of Sensors (-128 to 128)
    
    // Singleton
    private static var _shared:MultiMagnetometer?
    static var shared:MultiMagnetometer {
        _shared = _shared ?? MultiMagnetometer()
        return _shared!
    }
    
    // Delegate
    var delegate:MultiMagnetometerDelegate?
    
    override init() {
        super.init()
        
        // CoreLocation Setup +
        GPS.shared.set(updateHeadingCallback: updateHeading)
        GPS.shared.startTracking()
        
        // CoreMotion Setup ↑
        FluxSensor.shared.set(updateMotionCallback: updateMotion)
        FluxSensor.shared.set(updateGyroCallback: updateGyro)
        FluxSensor.shared.set(updateMagnetometerCallback: updateMagnetometer)
        FluxSensor.shared.startTracking()
        
    }
    
    private func updateHeading(_ heading:CLHeading?) -> Void {
        guard let heading = heading else { return }
        delegate?.updateMagneticHeading(x: heading.magneticHeading<180 ? -heading.magneticHeading : 360-heading.magneticHeading)
        
        let magnitude = sqrt(heading.x * heading.x + heading.y * heading.y + heading.z * heading.z)
        delegate?.updateHeading(x: heading.x, y: heading.y, z: heading.z, m: magnitude, s: 180)
    }
    private func updateMotion(_ data:CMDeviceMotion?) -> Void {
        guard let data = data else { return }
        
        delegate?.updateAttitude(roll: data.attitude.roll,
                                 yaw: data.attitude.yaw,
                                 pitch: data.attitude.pitch,
                                 matrix: data.attitude.rotationMatrix)
        
        var x = data.magneticField.field.x
        var y = data.magneticField.field.y
        var z = data.magneticField.field.z
        var magnitude = sqrt(x * x + y * y + z * z)
        delegate?.updateCalibratedMagneticHeading(x: x, y: y, z: z, m: magnitude, s: DELTA)
        
        x = data.userAcceleration.x
        y = data.userAcceleration.y
        z = data.userAcceleration.z
        magnitude = sqrt(x * x + y * y + z * z)
        delegate?.updateAcceleration(x: x, y: y, z: z, m: magnitude)
        
        x = data.gravity.x
        y = data.gravity.y
        z = data.gravity.z
        magnitude = sqrt(x * x + y * y + z * z)
        delegate?.updateGravity(x: x, y: y, z: z, m: magnitude)
    }
    private func updateGyro(_ data:CMGyroData?) -> Void {
        guard let data = data else { return }
        let magnitude = sqrt(data.rotationRate.x * data.rotationRate.x + data.rotationRate.y * data.rotationRate.y + data.rotationRate.z * data.rotationRate.z)
        delegate?.updateGyro(x: data.rotationRate.x, y: data.rotationRate.y, z: data.rotationRate.z, m: magnitude)
    }
    
    private func updateMagnetometer(_ data:CMMagnetometerData?) -> Void {
        guard let data = data else { return }
        let magnitude = sqrt(data.magneticField.x * data.magneticField.x + data.magneticField.y * data.magneticField.y + data.magneticField.z * data.magneticField.z)
        delegate?.updateMagnetometer(x: data.magneticField.x, y: data.magneticField.y, z: data.magneticField.z, m: magnitude, s: DELTA)
    }
}
