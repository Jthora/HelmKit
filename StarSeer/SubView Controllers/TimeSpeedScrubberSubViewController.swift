//
//  TimeSpeedScrubberSubViewController.swift
//  HelmKit
//
//  Created by Jordan Trana on 6/5/19.
//  Copyright © 2019 Jordan Trana. All rights reserved.
//

import UIKit
import SpriteKit

class TimeSpeedScrubberSubViewController: SubViewController, UIGestureRecognizerDelegate {
    
    let panGestureRecognizer:UIPanGestureRecognizer
    let timeSpeedLabel:UILabel
    
    var fold:Bool = false
    
    func toggleFold() {
        fold = !fold
        update()
    }
    
    var warp:TimeInterval {
        return TimeInterval(fold ? pow(timeSpeed, 2) : timeSpeed)
    }
    
    var timeSpeed:CGFloat = 1 {
        didSet {
            update()
        }
    }
    
    func update() {
        timeSpeedLabel.text = "Timespeed: \(String(format: "%.2f",timeSpeed))\(fold ? "x^2 (\(String(format: "%.2f",warp)))" : "x")"
    }
    
    static weak var `$`:TimeSpeedScrubberSubViewController? = nil
    
    init(wideNarrowContainerView:UIView, timeSpeedLabel:UILabel, panGestureRecognizer: UIPanGestureRecognizer) {
        self.panGestureRecognizer = panGestureRecognizer
        self.timeSpeedLabel = timeSpeedLabel
        super.init(view: wideNarrowContainerView)
        self.panGestureRecognizer.delegate = self
        TimeSpeedScrubberSubViewController.`$` = self
        update()
    }
    
    func timeSpeedGestureRecognizer(_ sender: UIPanGestureRecognizer) {
        let velocity = sender.velocity(in: self.view)
        timeSpeed += velocity.x / self.view.bounds.width
    }
}

