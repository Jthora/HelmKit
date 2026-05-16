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
    func didUpdate(_ astroTimer:AstroTimer, _ timePoint:AstroTimePoint)
}

class AstroTimer {
    
    var delegate:AstroTimerDelegate? = nil
    
    var timeVector:AstroTimeVector? {
        if timePointHistory.count == Int(sampleRate) {
            return AstroTimeVector(scale: sampleRate.toTimeInterval(), timePointA: timePointHistory.first!, timePointB: timePointHistory.last!)
        }
        return nil
    }
    var timePointHistory:[AstroTimePoint] = []
    func addTimePointToHistory(_ timePoint:AstroTimePoint) {
        timePointHistory.append(timePoint)
        if timePointHistory.count > Int(sampleRate) {
            timePointHistory.remove(at: 0)
        }
    }
    
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
        let timePoint = AstroTimePoint(date: Date())
        addTimePointToHistory(timePoint)
        delegate?.didUpdate(self, timePoint)
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

struct AstroTimeVector {
    let scale:TimeInterval = 1
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
    
    init(scale:TimeInterval = 1, timePointA:AstroTimePoint, timePointB:AstroTimePoint) {
        self.moon = timePointB.moon - timePointA.moon
        self.mercury = timePointB.mercury - timePointA.mercury
        self.venus = timePointB.venus - timePointA.venus
        self.earth = timePointB.earth - timePointA.earth
        self.mars = timePointB.mars - timePointA.mars
        self.jupiter = timePointB.jupiter - timePointA.jupiter
        self.saturn = timePointB.saturn - timePointA.saturn
        self.uranus = timePointB.uranus - timePointA.uranus
        self.neptune = timePointB.neptune - timePointA.neptune
        self.pluto = timePointB.pluto - timePointA.pluto
    }
    
    func degrees(for planet:Scaler.PlanetFocus) -> Degree {
        switch planet {
        case .moon: return moon
        case .mercury: return mercury
        case .venus: return venus
        case .earth: return earth
        case .mars: return mars
        case .jupiter: return jupiter
        case .saturn: return saturn
        case .uranus: return uranus
        case .neptune: return neptune
        case .pluto: return pluto
        }
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
    
    func degrees(for planet:Scaler.PlanetFocus) -> Degree {
        switch planet {
        case .moon: return moon
        case .mercury: return mercury
        case .venus: return venus
        case .earth: return earth
        case .mars: return mars
        case .jupiter: return jupiter
        case .saturn: return saturn
        case .uranus: return uranus
        case .neptune: return neptune
        case .pluto: return pluto
        }
    }
}

