//
//  Ticker.swift
//  HelmKit
//
//  Created by Jordan Trana on 11/4/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation

struct Tick {
    var date:Date
    var i:Int
    
}

class Ticker: AstroTimerDelegate {
    
    let scaler:Scaler
    
    init(scaler:Scaler) {
        self.scaler = scaler
        AstroTimer.addDelegate(delegate: self, priority: .first)
    }
    
    func didUpdate(_ astroTimer: AstroTimer, _ timePoint: AstroTimePoint) {
        
    }
}
