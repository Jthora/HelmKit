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
    func didUpdate(_ timePoint:AstroTimePoint)
}

class AstroTimer {
    static let shared = AstroTimer()
    
    var delegate:AstroTimerDelegate?
    
    var sampleRate:Hz = 60
    
    // distance range filters to define limits of how close planets must be (temporally or physically) to be added to the list of aspects
    var filterAngleLimit:Degree?
    var filterDistanceLimit:Meter?
    var filterDistanceTime:TimeInterval?
    
    var timer:Timer?
    private func _timerUpdate(_ timer:Timer) {
        update()
    }
    
    func update() {
        
        delegate?.didUpdate(AstroTimePoint(date: Date()))
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
    let moon:Degree
    let mercury:Degree
    let venus:Degree
    let earth:Degree
    let mars:Degree
    let jupiter:Degree
    let saturn:Degree
    let uranus:Degree
    let neptune:Degree
    let pluto:Degree
    
    init(date:Date) {
        self.date = date
        self.moon = Astronomy.moonPhaseAngle(on: date)
        self.mercury = Astronomy.orbitalProgression(.mercury, on: date)!
        self.venus = Astronomy.orbitalProgression(.venus, on: date)!
        self.earth = Astronomy.orbitalProgression(.earth, on: date)!
        self.mars = Astronomy.orbitalProgression(.mars, on: date)!
        self.jupiter = Astronomy.orbitalProgression(.jupiter, on: date)!
        self.saturn = Astronomy.orbitalProgression(.saturn, on: date)!
        self.uranus = Astronomy.orbitalProgression(.uranus, on: date)!
        self.neptune = Astronomy.orbitalProgression(.neptune, on: date)!
        self.pluto = Astronomy.orbitalProgression(.pluto, on: date)!
    }
}

