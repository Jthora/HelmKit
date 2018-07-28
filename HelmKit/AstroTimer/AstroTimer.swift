//
//  AstroTimer.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/28/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import SwiftAA

protocol AstroTimerDelegate {
    func didUpdate(_ nearbyTimePoints:[TimeInterval:AstroTimePoint])
}

class AstroTimer {
    static let shared = AstroTimer()
    
    var delegate:AstroTimerDelegate?
    
    var sampleRate:Hz = 30
    
    // distance range filters to define limits of how close planets must be (temporally or physically) to be added to the list of aspects
    var filterAngleLimit:Degree?
    var filterDistanceLimit:Meter?
    var filterDistanceTime:TimeInterval?
    
    var timer:Timer?
    private func _timerUpdate(_ timer:Timer) {
        update()
    }
    
    func update() {
        var nearbyTimePoints:[TimeInterval : AstroTimePoint] = [:]
        
        delegate?.didUpdate(nearbyTimePoints)
    }
    
    func start(_ hz:Hz? = nil) {
        guard timer?.isValid != true else { return }
        if let hz = hz { sampleRate = hz }
        timer = Timer.scheduledTimer(withTimeInterval: sampleRate.toTimeInterval(), repeats: true, block: _timerUpdate)
    }
    
    func stop() {
        timer?.invalidate()
    }
    
    func reset() {
        stop()
        start()
    }
    
}

struct AstroTimePoint {
    let date:Date
    let aspect:Astrology.Aspect
}
